'''A dynamic content management system using jQuery and Python'''

VERSION = (0, 9, 0)

def get_version():
    return '.'.join(map(str,VERSION))

# This list is updated by the views.appsite.appsite handler
empty_choice = ('','-----------------')


__version__   = get_version()
__license__   = "BSD"
__author__    = "Luca Sbardella"
__contact__   = "luca.sbardella@gmail.com"
__homepage__  = "http://djpcms.com/"
__docformat__ = "restructuredtext"

LIBRARY_NAME = 'djpcms'

import os
import sys

parentdir = lambda dir,up=1: dir if not up else\
                     parentdir(os.path.split(dir)[0],up-1)
DJPCMS_DIR = parentdir(os.path.abspath(__file__))
path_dir = parentdir(DJPCMS_DIR)


def DEFAULT_JAVASCRIPT():
    return ['djpcms/modernizr-1.7.min.js',
            'djpcms/jquery.cookie.js',
            'djpcms/form.js',
            'djpcms/showdown.js',
            'djpcms/djpcms.js']
    

def DEFAULT_STYLE_SHEET():
    return {'all':['http://yui.yahooapis.com/2.9.0/build/\
reset-fonts-grids/reset-fonts-grids.css']}


def install_lib(basepath, dirname, module_name = None):
    if module_name:
        try:
            return __import__(module_name)
        except ImportError:
            dir = os.path.join(basepath,dirname)
            sys.path.insert(0,dir)
            try:
                return __import__(module_name)
            except ImportError:
                pass
    else:
        dir = os.path.join(basepath,dirname)
        sys.path.insert(0,dir)
        
        
def install_libs():
    '''Install libraries to python Path if needed'''
    if path_dir not in sys.path:
        sys.path.insert(0,path_dir)
    dlibs = os.path.join(DJPCMS_DIR,'libs')
    py2py3 = install_lib(dlibs, 'py2py3', 'py2py3')
    if py2py3.ispy3k:
        install_lib(dlibs, 'jinja2_3', 'jinja2')
    else:
        install_lib(dlibs, 'jinja2', 'jinja2')

install_libs()

import py2py3
ispy3k = py2py3.ispy3k
to_string = py2py3.to_string
to_bytestring = py2py3.to_bytestring
is_string = py2py3.is_string
is_bytes_or_string = py2py3.is_bytes_or_string
UnicodeMixin = py2py3.UnicodeMixin


def init_logging(settings, clear_all = False):
    '''Initialise logging'''
    from djpcms.utils.log import dictConfig
    
    if clear_all:
        import logging
        logging.Logger.manager.loggerDict.clear()

    if settings:
        LOGGING = settings.LOGGING
        if LOGGING:
            if settings.DEBUG:
                handlers = ['console']
                if hasattr(settings, 'LOG_TO_FILE') and settings.LOG_TO_FILE:
                    if LOGGING['handlers'].has_key('file'):
                        handlers.append('file')
                LOGGING['handlers']['console']['level'] = 'DEBUG' 
                LOGGING['root'] = {
                                'handlers': handlers,
                                'level': 'DEBUG',
                                }
            dictConfig(settings.LOGGING)
        

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

HTML_CLASSES = {
    'ajax': 'ajax',
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
    'legend': 'legend ui-state-default ui-corner-all'
    }

from .core import *
from .utils import ajax
from .utils.decorators import *

def secret_key():
    '''Secret Key used as base key in encryption algorithm'''
    if sites.settings:
        return sites.settings.get('SECRET_KEY','sk').encode()
    else:
        return b'sk'
