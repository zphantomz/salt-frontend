from pyramid.view import view_config

@view_config(route_name='index', renderer='../templates/mytemplate.jinja2')
def view_index(request):
    return {'project': 'Saltstack Frontend'}

