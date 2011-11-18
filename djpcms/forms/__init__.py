'''\
A lightweight form library crucial not only for browser driven
applications, but also for validating remote procedure calls
and command line inputs.

The main class in this module is :class:`Form`.
It encapsulates a sequence of form fields (subclasses of
:class:`Field`) and a collection of validation
rules that must be fulfilled in order for the form to be accepted.

Form classes are created as subclasses of :class:`Form`
and make use of a declarative style similar to django_'s forms.

.. _django: http://www.djangoproject.com/
'''
from .html import *
from .globals import *
from .fields import *
from .base import *
from .formsets import *