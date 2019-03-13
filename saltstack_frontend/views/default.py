from pyramid.view import view_config

@view_config(route_name='index', renderer='../templates/mytemplate.jinja2')
def view_index(request):
    return {'project': 'Saltstack Frontend'}

@view_config(route_name='minions', renderer='../templates/mytemplate.jinja2')
def view_minions(request):
    return {'project': 'Saltstack Frontend'}

