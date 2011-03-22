# Uniforms Layout is the Default layout
from uuid import uuid4

from djpcms.core.exceptions import DjpcmsException
from .layout.uniforms import Layout as DefaultLayout

__all__ = ['FormException',
           'ValidationError',
           'DefaultLayout',
           'generate_prefix',
           'get_submit_key',
           'SAVE_KEY',
           'CANCEL_KEY',
           'SAVE_AND_CONTINUE_KEY',
           'SAVE_AS_NEW_KEY',
           'PREFIX_KEY',
           'REFERER_KEY']


# some useful hidden keys
SAVE_KEY = '_save'
CANCEL_KEY = '_cancel'
SAVE_AND_CONTINUE_KEY = '_save_and_continue'
SAVE_AS_NEW_KEY = '_save_as_new'
PREFIX_KEY = '__prefixed__'
REFERER_KEY = '__referer__'


class FormException(DjpcmsException):
    pass


class ValidationError(Exception):
    pass


def generate_prefix():
    return str(uuid4())


class NoData(object):
    def __repr__(self):
        return '<NoData>'
    __str__ = __repr__


def get_submit_key(data, key):
    prefix = data.get(PREFIX_KEY,None)
    submit_key = data.get(key, None)
    if submit_key:
        if prefix and prefix in submit_key:
            submit_key = submit_key[len(prefix):]
    return submit_key


nodata = NoData()
