import subprocess
import yaml
from functools import lru_cache
import logging
from ast import literal_eval
import glob

log = logging.getLogger(__name__)

@lru_cache(maxsize=2)
def get_jobs():
    cmd = ['sudo', 'salt-run', 'jobs.list_jobs', 'search_function="state.apply"', '--output=raw']
    out = subprocess.run(cmd, stdout=subprocess.PIPE)
    try:
        data = literal_eval(out.stdout.decode('utf8'))
    except Exception as e:
        log.warn("Error ({}) retrieving jobs with command {}".format(e, ' '.join(cmd)))
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
    except Exception as e:
        log.warn("Error ({}) retrieving job detail with command {}".format(e, ' '.join(cmd)))
        return {}
    return data


@lru_cache(maxsize=2)
def get_minions():
    """ Get standard minions and salt-ssh minions
    output:
      minions dict(): {'minions': {'name': data}
                       'ssh-minions': {'name': data}
                   }
    """
    minions = dict()
    # Load salt minion
    out = subprocess.run(['sudo', 'salt-run', 'manage.present', '--output=raw'],
                         stdout=subprocess.PIPE)
    try:
        data = literal_eval(out.stdout.decode('utf8'))
    except Exception as e:
        log.warn("Error ({}) retrieving minions with command {}".format(e, ' '.join(cmd)))
        return {}
    minions['minions'] = data

    # Load ssh-minion from roster file (hardcoded on /etc/salt/roster)
    try:
        with open("/etc/salt/roster", "r") as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
    except Exception as e:
        log.warn("Error ({}) during roster file parsing")
        data = {}
    minions['ssh-minions'] = data
    
    return minions

@lru_cache(maxsize=2)
def get_nodegroups():
    """ Get list of nodegroups and matched minions (work only with minion-id pattern matching)
    output:
      nodegroups dict(): {'nodegroups': {'name': list}
                          'ssh_list_nodegroups': {'name': list}
                         }
    """
    nodegroups = dict()
    salt_config_files = glob.glob("/etc/salt/master.d")
    for file in salt_config_files:
        try:
            with open(file, "r") as f:
                data = yaml.load(f, Loader=yaml.SafeLoader)
        except Exception as e:
            log.warning("Error ({}) during file parsing".format(e))
        if 'nodegroups' in data.keys():
            nodegroups['nodegroups'] = data['nodegroups']
        if 'ssh_list_nodegroups' in data.keys():
            nodegroups['ssh_list_nodegroups'] = data['ssh_list_nodegroups']

    return nodegroups