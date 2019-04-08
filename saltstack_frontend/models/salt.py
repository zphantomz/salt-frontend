import subprocess
import yaml
from functools import lru_cache
import logging
from ast import literal_eval

nodegroup_files = "/etc/salt/master.d/groups.conf"
ssh_nodegroup_files = "/etc/salt/master.d/ssh_groups.conf"

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
      nodegroups dict(): {'minions': {'name': data}
                          'ssh-minions': {'name': data}
                         }
    """
    nodegroups = dict()
    try:
        with open(nodegroup_files, "r") as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
    except Exception as e:
        log.warn("Error ({}) during nodegroups file parsing")
        data = {'nodegroups': dict()}    
    nodegroups['nodegroups'] = data['nodegroups']
    try:
        with open(ssh_nodegroup_files, "r") as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
    except Exception as e:
        log.warn("Error ({}) during ssh nodegroups file parsing")
        data = {'ssh_list_nodegroups': dict()}
    nodegroups['ssh_list_nodegroups'] = data['ssh_list_nodegroups']

    return nodegroups