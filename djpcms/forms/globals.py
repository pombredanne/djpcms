# Uniforms Layout is the Default layout
from uuid import uuid4

from djpcms.core.exceptions import DjpcmsException
from .layout.uniforms import Layout as DefaultLayout

__all__ = ['FormException',
           'ValidationError',
           'DefaultLayout',
           'generate_prefix']


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


nodata = NoData()
