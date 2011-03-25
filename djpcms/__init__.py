'''A dynamic content management system using jQuery and Python'''

VERSION = (0, 9, 'dev')

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
libs = []


def install_lib(basepath, dirname, module_name):
    try:
        __import__(module_name)
    except ImportError:
        dir = os.path.join(basepath,dirname)
        sys.path.insert(0,dir)
        try:
            module = __import__(module_name)
            libs.append(module)
        except ImportError:
            pass
        
        
def install_libs():
    if path_dir not in sys.path:
        sys.path.insert(0,path_dir)
    dlibs = os.path.join(DJPCMS_DIR,'libs')
    install_lib(dlibs, 'py2py3', 'py2py3')
    install_lib(dlibs, 'medplate', 'medplate')
    install_lib(dlibs, 'django-tagging', 'tagging')
    install_lib(dlibs, 'flowrepo', 'flowrepo')
    #install_lib(dlibs, 'BeautifulSoup', 'BeautifulSoup')

install_libs()

import py2py3
ispy3k = py2py3.ispy3k
to_string = py2py3.to_string
to_bytestring = py2py3.to_bytestring
is_string = py2py3.is_string
UnicodeMixin = py2py3.UnicodeMixin

from .apps import *
from .apps.management import execute
from .http import serve
from .conf import nodata


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
        

def init_logging(settings, clear_all = True):
    '''Initialise logging'''
    from djpcms.utils.log import dictConfig
    
    if clear_all:
        import logging
        logging.Logger.manager.loggerDict.clear()

    settings = sites.settings
    if settings:
        if settings.DEBUG:
            settings.LOGGING['root'] = {
                                        'handlers': ['console'],
                                        'level': 'DEBUG',
                                        }
        dictConfig(settings.LOGGING)
        


