from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from .. import models


@view_config(route_name='jobs', renderer='../templates/jobs_list.jinja2')
def view_jobs(request):
    refresh = request.params.get('refresh', None)
    if refresh:
        models.salt.get_jobs.cache_clear()
        return HTTPFound(request.route_url('jobs'))
    jobs = models.salt.get_jobs()
    return {'jobs': jobs}


@view_config(route_name='job_details', renderer='../templates/mytemplate.jinja2')
def view_job_details(request):
    job_id = request.matchdict['id']
    title = job_id
    #jobs = models.salt.get_jobs()
    return {}