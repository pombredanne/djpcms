'''
While the :class:`djpcms.forms.Form` class handles the validation logic of an
input form which can be used across a wide range of applications, form layouts,
introduced in this section, are an HTML specific utility for rendering forms
according to user specified layouts.

A form layout is a subclass of :class:`FormLayout`,
and it is composed of :class:`FormLayoutElement` components.
The :mod:`djpcms.forms.layout` uses the :mod:`djpcms.html` library to
construct flexible and powerful classes for rendering forms in any shape or
form.
'''
from .classes import *
from .base import *
from .table import *