from pyramid.view import view_config
from .. import models

@view_config(route_name='index', renderer='../templates/index.jinja2')
def view_index(request):
    return {'project': 'Saltstack Frontend'}


@view_config(route_name='minions', renderer='../templates/minions.jinja2')
def view_minions(request):
    # get config file from registry
    nodegroups_config_files = request.registry.settings.get('saltstack.nodegroup_file')
    ssh_nodegroups_config_files = request.registry.settings.get('saltstack.ssh_nodegroup_file')
    print(nodegroups_config_files, ssh_nodegroups_config_files)
    minions = models.salt.get_minions()
    nodegroups = models.salt.get_nodegroups(nodegroups_config_files, ssh_nodegroups_config_files)
    return {'minions': minions,
            'nodegroups': nodegroups
            }


@view_config(route_name='pillars', renderer='../templates/pillars.jinja2')
def view_pillars(request):
    import glob
    pillar_files = glob.glob("/srv/pillar/*.sls")
    return {'pillar_files': pillar_files}
