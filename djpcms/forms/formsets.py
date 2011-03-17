from djpcms.html import HiddenInput

from .base import Form, UnicodeMixin
from .fields import IntegerField

__all__ = ['FormSet']
        
        
class FormSet(UnicodeMixin):
    
    def __init__(self, form_class):
        self.form_class = form_class
        