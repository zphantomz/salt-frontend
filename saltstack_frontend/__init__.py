from pyramid.config import Configurator
import configparser

__version__ = "0.1"

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.include('.routes')
        config.include('.models')
        config.scan()
    return config.make_wsgi_app()
