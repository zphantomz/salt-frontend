from pyramid.static import QueryStringConstantCacheBuster
from . import __version__


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_cache_buster(
        'static',
        QueryStringConstantCacheBuster(__version__))
    config.add_route('index', '/')
    config.add_route('minions', '/minions')
    config.add_route('pillars', '/pillars')
    config.add_route('jobs', '/jobs')
    config.add_route('job_details', '/jobs/{id}')
