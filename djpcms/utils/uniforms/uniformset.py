from django.forms.forms import BoundField

from djpcms.utils import form_kwargs, force_unicode, mark_safe


class ModelFormInlineHelper(object):
    '''Inline formset helper for model with foreign keys.'''
    def __init__(self, parent_model, model, legend = None, **kwargs):
        from django.forms.models import inlineformset_factory
        self.parent_model = parent_model
        self.model   = model
        if legend is not False:
            legend = legend or force_unicode(model._meta.verbose_name_plural)
        self.legend = mark_safe('' if not legend else '<legend>'+legend+'</legend>')
        self.FormSet = inlineformset_factory(parent_model, model, **kwargs)
        
    def get_default_prefix(self):
        return self.FormSet.get_default_prefix()
    
    def queryset(self, request):
        return self.model._default_manager.all()
    
    def get_formset(self, request = None, instance = None, prefix = None):
        formset = self.FormSet(**form_kwargs(request  = request,
                                             instance = instance,
                                             prefix   = prefix,
                                             queryset = self.queryset(request)))
        return FormsetWrap(formset,self.legend)
    

class FormsetWrap(object):
    
    def __init__(self, formset, legend):
        self.formset = formset
        self.legend  = legend
        
    def __iter__(self):
        for form in self.formset.forms:
            yield form
            
    def is_valid(self):
        return self.formset.is_valid()
    
    def __can_delete(self):
        return self.formset.can_delete
    can_delete = property(__can_delete)
    
    def field_count(self):
        fields = list(self.fields())
        n = len(fields)+1
        if self.can_delete:
            n += 1
        return n
        #num_of_fields = 0
        #if self.has_auto_field():
        #    num_of_fields += 1
        #num_of_fields += len(self.fieldsets[0][1]["fields"])
        #if self.formset.can_order:
        #    num_of_fields += 1
        #if self.formset.can_delete:
        #    num_of_fields += 1
        #return num_of_fields
        
    def fields(self):
        formset = self.formset
        form    = formset.form
        fk = getattr(formset, "fk", None)
        for name,field in formset.form.base_fields.items():
            if fk and fk.name == name:
                continue
            #bound_field = BoundField(form, field, name)
            if field.label is None:
                field.label = force_unicode(name.replace('_',' '))
            yield field

