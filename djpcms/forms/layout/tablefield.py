from djpcms.html import table_header, Widget
from djpcms.utils.text import nicename

from .base import FieldTemplate
from .table import TableFormElement, TableRow


__all__ = ['TableRelatedFieldset']

    
class TableRelatedFieldset(TableFormElement):
    '''A :class:`djpcms.forms.layout.TableFormElement`
class for handling ralated :class:`djpcms.forms.FieldSet`.'''

    def __init__(self, form, formset, fields=None, **kwargs):
        self.formset = formset
        self.form_class = form.base_inlines[formset].form_class
        headers = list(self.get_heads(fields))
        super(TableRelatedFieldset,self).__init__(headers, **kwargs)
        self.row_maker = TableRow(*self.fields)
        self.row_maker.check_fields(list(self.fields))
        
    def get_heads(self, fields):
        headers = list(fields or ())
        dfields = self.form_class.base_fields
        self.hidden_fields = []
        for field in dfields:
            if field not in headers:
                headers.append(field)
        for name in headers:
            field = dfields.get(name)
            if field:
                if field.is_hidden:
                    self.hidden_fields.append(
                        FieldTemplate(internal={'field':name}))
                else:
                    label = field.label or nicename(name)
                    extraclass = 'required' if field.required else None
                    yield table_header(name,
                                       label,
                                       field.help_text,
                                       extraclass=extraclass)
         
    def row_generator(self, request, widget, context):
        formset = widget.form.form_sets[self.formset]
        for form in formset.forms:
            row = self.child_widget(self.row_maker, widget, form=form)
            yield row.render(request)
    
    def stream(self, request, widget, context):
        for data in super(TableRelatedFieldset,self).stream(request,\
                                                    widget, context):
            yield data
        formset = widget.form.form_sets[self.formset]
        # Loop over hidden fields
        if self.hidden_fields:
            for form in formset.forms:
                for field in self.hidden_fields:
                     child = self.child_widget(field, widget, form=form)
                     yield child.render(request)
        # the number of forms
        yield formset.num_forms().render(request)
    

