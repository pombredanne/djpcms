from .base import Form, UnicodeMixin
from .fields import IntegerField
from .html import HiddenInput

__all__ = ['FormSet']
        
        
class FormSet(UnicodeMixin):
    
    def __init__(self, form_class):
        self.form_class = form_class
        