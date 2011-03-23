'''\
A lightweight form library crucial not only for browser driven
application, but also for RPC and command line, driven applications.

The main class in this module is :class:`djpcms.forms.Form`.
A Form object encapsulates a sequence of form fields and a
collection of validation rules that must be fulfilled in
order for the form to be accepted.
Form classes are created as subclasses of :class:`djpcms.forms.Form`
and make use of a declarative style
similar to django_'s forms.

.. _django: http://www.djangoproject.com/
'''
from .html import *
from .globals import *
from .fields import *
from .base import *
from .formsets import *