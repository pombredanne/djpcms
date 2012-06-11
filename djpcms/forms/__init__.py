'''\
A lightweight form library crucial not only for browser driven
applications, but also for validating remote procedure calls (RPC)
and command line inputs.

The main class in this module is :class:`Form`.
It encapsulates a sequence of form :class:`Field`
and a collection of validation rules that must be fulfilled in order
for the form to be accepted.

Form classes are created as subclasses of :class:`Form`
and make use of a declarative style similar to django_'s forms.

A :class:`Form` is rendered into ``html`` via the :class:`HtmlForm`.
For example, this is a form for submitting an issue::

    from djpcms import forms
    
    class IssueForm(forms.Form):
        name = forms.CharField()
        description = forms.CharField(widget = forms.TextArea(),
                                      required= False)
        labels = forms.CharField(required=False)
        
        
And this could be its :class:`HtmlForm` representation::

    IssueFormHtml = forms.HtmlForm(
        IssueForm,
        method = 'post'
    )

As you can see, no much has been specified in this declaration. Sensible
defaults are used.

This module dependos on :mod:`djpcms.html`.

.. _django: http://www.djangoproject.com/
'''
from .globals import *
from .html import *
from .fields import *
from .base import *
from .formsets import *
