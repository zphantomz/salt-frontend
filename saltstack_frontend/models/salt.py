import subprocess
import json
from functools import lru_cache
import logging
from ast import literal_eval

log = logging.getLogger(__name__)

@lru_cache(maxsize=2)
def get_jobs():
    cmd = ['sudo', 'salt-run', 'jobs.list_jobs', 'search_function="state.apply"', '--output=raw']
    out = subprocess.run(cmd, stdout=subprocess.PIPE)
    try:
        data = literal_eval(out.stdout.decode('utf8'))
    except ValueError:
        log.warn("Error retrieving jobs with command {}".format(cmd.join(' ')))
        return {}
    return data


@lru_cache(maxsize=32)
def get_job(job_id):
    """ Get info about a single job. Using literal_eval istead of json cause a common error on the 
    json salt output module that give an exception with non pure ascii characters
    params:
      job_id: numeric id of job
    output:
      dict(): job info.
    """
    cmd = ['sudo', 'salt-run', 'jobs.list_job', job_id, '--output=raw']
    out = subprocess.run(cmd, stdout=subprocess.PIPE)
    try:
        data = literal_eval(out.stdout.decode('utf8'))
    except ValueError:
        log.warn("Error retrieving job detail with command {}".format(cmd.join(' ')))
        return {}
    return data


@lru_cache(maxsize=2)
def get_minions():
    out = subprocess.run(['sudo', 'salt-run', 'manage.present', '--output=json'],
                         stdout=subprocess.PIPE)
    try:
        data = json.loads(out.stdout.decode('utf8'))
    except ValueError:
        return {}
    return data
