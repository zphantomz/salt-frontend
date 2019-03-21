from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from .. import models

import pprint


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
        job_failed = False
        if 'return' in job_data['Result'][minion]['return']:
            # salt-ssh put return inside other return
            job_result = job_data['Result'][minion]['return']
        else:
            job_result = job_data['Result'][minion]

        if isinstance(job_result, str):
            # ssh minions that give error immediately at first connection
            log.info("Minion {} return with error".format(minion))
            minion_job_data = [job_result]
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

                    # Analize step by step order them by __run_num__ and mark failed and warning step
                    minion_job_data = dict()
                    for step, step_data in job_result['return'].items():
                        # Find failed steps based on cmd.run (must evaluate retcode)
                        if 'retcode' in step_data['changes']:
                            if not step_data['changes']['retcode'] == 0:
                               step_data['result'] = False
                               job_failed = True
                        minion_job_data[job_result['return'][step]['__run_num__']] = step_data
                        minion_job_data[job_result['return'][step]['__run_num__']]['step_id'] = step.split('_|-')[1]

        if not job_failed:
            minions_done_ok += 1

        minions_job_result[minion] = {'data': minion_job_data,
                                      'num_steps': num_steps,
                                      'failed': job_failed
                                      }

    return {'minion_id': minion_id,
            'minions_total': len(minions_job_result),
            'minions_failed': len(minions_job_result) - minions_done_ok,
            'minions_job_result': minions_job_result
            }
