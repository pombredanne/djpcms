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

parentdir = lambda dir,up=1: dir if not up else parentdir(os.path.split(dir)[0],up-1)
DJPCMS_DIR = parentdir(os.path.abspath(__file__))
path_dir = parentdir(DJPCMS_DIR)


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
    install_lib(dlibs, 'medplate', 'medplate')
    if py2py3.ispy3k:
        install_lib(dlibs, 'jinja2_3', 'jinja2')
    else:
        install_lib(dlibs, 'jinja2', 'jinja2')
    install_lib(dlibs, 'djpapps')

install_libs()

import py2py3
ispy3k = py2py3.ispy3k
to_string = py2py3.to_string
to_bytestring = py2py3.to_bytestring
is_string = py2py3.is_string
UnicodeMixin = py2py3.UnicodeMixin


def node(path):
    '''Retrive a :class:`Node` from the global sitemap from a ``path`` input.
If the path is not available but its parent path is,
it returns a new node without storing it in the sitemap.
Otherwise it raises a :class:`djpcms.core.exceptions.PathException`.

:parameter path: node path.
'''
    return sites.tree[path]


def get_page(path):
    return sites.tree.get_page(path)
        

def init_logging(settings, clear_all = False):
    '''Initialise logging'''
    from djpcms.utils.log import dictConfig
    
    if clear_all:
        import logging
        logging.Logger.manager.loggerDict.clear()

    if settings:
        LOGGING = settings.LOGGING
        if settings.DEBUG:
            LOGGING['handlers']['console']['level'] = 'DEBUG' 
            LOGGING['root'] = {
                            'handlers': ['console'],
                            'level': 'DEBUG',
                            }
        dictConfig(settings.LOGGING)
        

LOGGING_SAMPLE = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s | (p=%(process)s,t=%(thread)s) | %(levelname)s | %(name)s | %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'silent': {
            'class': 'djpcms.utils.log.NullHandler',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'djpcms.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends':{
            'handlers': ['silent'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

from .core.exceptions import *
from .apps import *
from .apps.management import execute
from .conf import nodata
from .utils import ajax
from .utils.decorators import *

def secret_key():
    '''Secret Key used as base key in encryption algorithm'''
    if sites.settings:
        return sites.settings.get('SECRET_KEY','sk').encode()
    else:
        return b'sk'
    