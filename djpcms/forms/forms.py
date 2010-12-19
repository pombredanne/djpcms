from djpcms.conf import settings
from django import forms
from django.forms import models 
from django.forms.forms import get_declared_fields


__all__ = ['BaseForm',
           'Form',
           'ModelForm',
           'ValidationError',
           'model_to_dict',
           'MediaDefiningClass',
           'get_declared_fields',
           'modelform_factory']


BaseForm = forms.BaseForm
ValidationError = forms.ValidationError
model_to_dict = forms.model_to_dict
MediaDefiningClass = forms.MediaDefiningClass


class Form(forms.Form):
    '''A slight modification on django Form'''
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance',None)
        kwargs.pop('save_as_new',None)
        self.request = kwargs.pop('request',None)
        super(Form,self).__init__(*args, **kwargs)


class ModelForm(forms.ModelForm):
    '''A slight modification on django Form'''
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request',None)
        save_as_new = kwargs.pop('save_as_new',False)
        super(ModelForm,self).__init__(*args, **kwargs)
        if save_as_new:
            self.instance = self.instance.__class__()
        
        
def modelform_factory(model, form=ModelForm, **kwargs):
    return models.modelform_factory(model, form=form, **kwargs)

