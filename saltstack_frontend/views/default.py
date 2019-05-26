from pyramid.view import view_config
from .. import models


@view_config(route_name='index', renderer='../templates/index.jinja2')
def view_index(request):
    """ Home Page
    load some statistics from models and show as fancy tabs
    """
    jobs = models.salt.get_jobs()
    minions = models.salt.get_minions()
    pillars = models.salt.get_pillar_files()
    return {'jobs': jobs,
            'minions': minions,
            'pillars': pillars
            }


@view_config(route_name='minions', renderer='../templates/minions.jinja2')
def view_minions(request):
    # get config file from registry
    nodegroups_config_files = request.registry.settings.get(
        'saltstack.nodegroup_file')
    ssh_nodegroups_config_files = request.registry.settings.get(
        'saltstack.ssh_nodegroup_file')
    minions = models.salt.get_minions()
    nodegroups = models.salt.get_nodegroups(
        nodegroups_config_files, ssh_nodegroups_config_files)
    return {'minions': minions,
            'nodegroups': nodegroups
            }


@view_config(route_name='pillars', renderer='../templates/pillars.jinja2')
def view_pillars(request):
    import glob
    pillar_files = glob.glob("/srv/pillar/*.sls")
    return {'pillar_files': pillar_files}
