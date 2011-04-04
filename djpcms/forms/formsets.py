from copy import copy

from djpcms import UnicodeMixin
from djpcms.html import HiddenInput

from .fields import IntegerField

__all__ = ['FormSet']
        
        
class FormSet(UnicodeMixin):
    creation_counter = 0
    NUMBER_OF_FORMS_CODE = 'NUMBER_OF_FORMS'
    
    def __init__(self, form_class, initial_length = 3):
        self.form_class = form_class
        self.name = None
        self.creation_counter = FormSet.creation_counter
        self.initial_length = initial_length
        FormSet.creation_counter += 1
        self.form = None
    
    def __call__(self, form):
        fset = copy(self)
        fset.form = form
        return fset
    
    @property
    def is_bound(self):
        if self.form:
            return self.form.is_bound
        else:
            return False
        
    @property
    def errors(self):
        self._unwind()
        return self._errors
    
    @property
    def forms(self):
        self._unwind()
        return self._forms
    
    def _unwind(self):
        form = self.form
        if form is None:
            raise ValueError('Form not specified')
        prefix = '{0}_{1}_'.format(form.prefix or '',self.name)
        errors = self._errors = {}
        forms = self._forms = []
        is_bound = self.is_bound
        nf = '{0}{1}'.format(prefix,self.NUMBER_OF_FORMS_CODE) 
        if is_bound:
            if nf not in form.rawdata:
                raise ValidationError('Could not find number of "{0}" forms'.format(self.name))
            num_forms = int(form.rawdata[nf])
        else:
            num_forms = self.initial_length
            
        self.num_forms = HiddenInput(name = nf, value = num_forms)
        
        for i in range(num_forms):
            f = self.get_form(prefix, i)
            forms.append(f)
            errors.update(f.errors)
            
    def get_form(self, prefix, idx):
        form = self.form
        prefix = '{0}{1}_'.format(prefix,idx)
        f = self.form_class(prefix = prefix,
                            data = form.rawdata,
                            request = form.request,
                            initial = form.initial)
        if not f.is_valid():
            if not f.changed:
                f._errors = {}
        return f
        

        