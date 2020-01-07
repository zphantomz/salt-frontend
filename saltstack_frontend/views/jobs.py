from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPFound
from .. import models

import re

import logging
log = logging.getLogger(__name__)

# Regexp used in frontend to show some steps as failed with a yellow "warn" background
warn_step_regexp = re.compile(".*not_present$|^WARN|^FAIL")

@view_config(route_name='jobs', renderer='../templates/jobs_list.jinja2')
def view_jobs(request):
    """ List all done jobs. using jobs.list_jobs salt command line utility
    To avoid to much system calls the function cache the results via lru cache.
    params:
      refresh: GET or POST parameter to clear lru cache.
    return:
      list of jobs in pure salt-run output format or empty dict
    """
    refresh = request.params.get('refresh', None)
    if refresh:
        models.salt.get_jobs.cache_clear()
        models.salt.get_job.cache_clear()
        return HTTPFound(request.route_url('jobs'))
    jobs = models.salt.get_jobs()
    return {'jobs': jobs}


@view_config(route_name='job_details', renderer='../templates/job_details.jinja2')
def view_job_details(request):
    """ Extract info about a single jobs using jobs.list_jobs salt command line utility
    do some preprocessing steps, cause different output structure from salt and salt-ssh
    job results.
    params:
      id: url path parameter, referred to salt job id
      minion: GET parameter, optional name of the minion to see job results
    return:
      job_result: {'return': <value> } where value can be:

    """
    minions_job_result = dict()
    minions_done_ok = 0
    job_id = request.matchdict['id']
    minion_id = request.params.get('minion', None)

    # get output of salt-run jobs.list_job command
    job_data = models.salt.get_job(job_id)

    for minion in job_data.get('Minions', {}):
        num_steps = 0
        steps_fail = 0
        steps_warn = 0
        minion_job_data = dict()
        job_failed = False
        if not minion in job_data['Result'].keys():
            # Handle minions without any return
            job_result = "Minion not return"
        elif 'return' in job_data['Result'][minion]['return']:
            # salt-ssh put return inside other return key
            job_result = job_data['Result'][minion]['return']
        else:
            job_result = job_data['Result'][minion]

        # ssh minions that give error immediately at first connection
        if isinstance(job_result, str):
            log.info("Minion {} return with error".format(minion))
            minion_job_data = [job_result]
            job_failed = True

        # minion that received wrong commands (like states not found)
        elif isinstance(job_result['return'], list):
            log.info("Minion {} return with error".format(minion))
            minion_job_data = [job_result['return'][0]]
            job_failed = True

        # minion with no return
        elif isinstance(job_result['return'], str):
            log.info("Minion {} return with error".format(minion))
            minion_job_data = ["No Return"]
            job_failed = True

        else:
            if isinstance(job_result['return'], dict):
                if '_error' in job_result['return']:
                    # ssh minion that give error in returning data
                    minion_job_data = [job_result['return']['stderr']]
                    job_failed = True

                elif 'error' in job_result['return']:
                    # minion that give error in returning data (like utf8 encoding)
                    minion_job_data = [job_result['return']]
                    job_failed = True

                else:
                    num_steps = len(job_result['return'].keys())
                    # Analize step by step and mark failed and warning step
                    for step, step_data in job_result['return'].items():
                        # Alwais force a step name, not based on __id__ key, that some time is missing...
                        step_id = step.split('_|-')[1]

                        # Steps based on cmd.run (must evaluate retcode to find failed steps)
                        if 'retcode' in step_data['changes']:
                            if not step_data['changes']['retcode'] == 0:
                               step_data['result'] = 'failed'
                               log.debug("Step marked as failed: {}".format(step_data))
                               steps_fail += 1

                        # Handle minion who give exception
                        elif not '__run_num__' in job_result['return'][step]:
                            step_data['result'] = 'failed'
                            log.debug("Step marked as failed: {}".format(step_data))
                            job_result['return'][step]['__run_num__'] = (1000 + steps_fail)
                            steps_fail += 1

                        # Steps not executed (require, onfail etc...)
                        elif not 'duration' in job_result['return'][step]:
                            step_data['result'] = 'info'

                        # Other steps who return False (Failed steps), on the first loop
                        # it evaluate salt-run output, but it change from False to failed to be
                        # compatible with other check, maybe it need to be do better...
                        elif step_data['result'] == False or step_data['result'] == 'failed':
                            step_data['result'] = 'failed'
                            steps_fail += 1
                        else:
                            pass

                        # Steps where id match warning regex string
                        if re.match(warn_step_regexp, step_id):
                            steps_warn += 1
                            # decrease failed count (it became only warning)
                            if step_data['result'] == 'failed':
                                steps_fail -= 1
                            step_data['result'] = 'warn'
                        if steps_fail > 0:
                            job_failed = True

                        minion_job_data[job_result['return'][step]['__run_num__']] = step_data
                        minion_job_data[job_result['return'][step]['__run_num__']]['step_id'] = step_id

        if not job_failed:
            minions_done_ok += 1
        #log.info("Minion: {} job_failed: {}".format(minion, job_failed))

        minions_job_result[minion] = {'data': minion_job_data,
                                      'num_steps': num_steps,
                                      'failed': job_failed,
                                      'steps_fail': steps_fail,
                                      'steps_warn': steps_warn
                                      }
    # save jobs output as txt
    if request.params.get('output', None) == 'txt' and minion_id:
        res = render("../templates/job_details_txt.jinja2",
                     {'minion_id': minion_id,
                      'minions_job_result': minions_job_result},
                      request=request)
        response = Response(res)
        response.content_type = 'text/plain'
        return response

    return {'minion_id': minion_id,
            'minions_total': len(minions_job_result),
            'minions_failed': len(minions_job_result) - minions_done_ok,
            'minions_job_result': minions_job_result
            }
