import subprocess
import json
from functools import lru_cache
import logging

log = logging.getLogger(__name__)

@lru_cache(maxsize=2)
def get_jobs():
    cmd = ['sudo', 'salt-run', 'jobs.list_jobs', 'search_function="state.apply"', '--output=json']
    out = subprocess.run(cmd, stdout=subprocess.PIPE)
    try:
        data = json.loads(out.stdout.decode('utf8'))
    except ValueError:
        log.warn("Error retrieving jobs with command {}".format(cmd.join(' ')))
        return {}
    return data


@lru_cache(maxsize=32)
def get_job(job_id):
    cmd = ['sudo', 'salt-run', 'jobs.list_job', job_id, '--output=json']
    out = subprocess.run(cmd, stdout=subprocess.PIPE)
    try:
        data = json.loads(out.stdout.decode('utf8'))
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
