'''A dynamic content management system using jQuery and Python'''
VERSION = (0, 9, 0)


# This list is updated by the views.appsite.appsite handler
empty_choice = ('','-----------------')


__version__   = '.'.join(map(str,VERSION))
__license__   = "BSD"
__author__    = "Luca Sbardella"
__contact__   = "luca.sbardella@gmail.com"
__homepage__  = "http://djpcms.com/"
__docformat__ = "restructuredtext"


import os
import sys

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARY_NAME = os.path.basename(PACKAGE_DIR)
SOFTWARE_NAME = LIBRARY_NAME + ' ' +  __version__


def DEFAULT_JAVASCRIPT(*extra):
    js = ['djpcms/jquery.cookie.js',
          'djpcms/jquery.form.js',
          'djpcms/showdown.js',
          'djpcms/djpcms.js',
          'djpcms/button.js',
          'djpcms/autocomplete.js']
    js.extend(extra)
    return js


LOGGING_SAMPLE = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s | (p=%(process)s,t=%(thread)s)\
 | %(levelname)s | %(name)s | %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'simple_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'djpcms.request':{
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

class Renderer(object):
    '''A mixin for all classes which render into string or bytes.

.. attribute:: description

    An optional description of the renderer.
    
    Default ``None``
'''
    description = None
    
    def render(self, request=None, **kwargs):
        '''render ``self`` as a string or bytes.'''
        raise NotImplementedError()
    
    def content_type(self):
        '''Content Type for this renderer'''
        return 'text/plain' 
    
    def media(self, request):
        '''It returns an instance of :class:`djpcms.media.Media` or ``None``.
It should be overwritten by derived classes.'''
        return None
    
def is_renderer(obj):
    return isinstance(obj, Renderer)
    
HTML = {
    'ajax': 'ajax',
    'button': 'btn',
    'post_view_key': 'xhr',
    'errorlist': 'errorlist',
    'formmessages': 'form-messages',
    'multi_autocomplete_class': 'multi',
    'calendar_class': 'dateinput',
    'currency_input': 'currency-input',
    'edit': 'editable',
    'delete': 'deletable',
    'objectdef': 'object-definition',
    'main_nav': 'main-nav',
    'link_active': 'ui-state-active',
    'link_default': '',
    'secondary_in_list': 'secondary',
    'error': 'status-error',
    'legend': 'legend ui-state-default ui-corner-all'
    }

def secret_key():
    '''Secret Key used as base key in encryption algorithm'''
    if sites.settings:
        return sites.settings.get('SECRET_KEY','sk').encode()
    else:
        return b'sk'
