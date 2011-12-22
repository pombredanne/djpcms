from djpcms.html import table_header, Widget
from djpcms.utils.text import nicename

from .table import TableFormElement, TableRow


__all__ = ['TableRelatedFieldset']

    
class TableRelatedFieldset(TableFormElement):
    '''A :class:`djpcms.forms.layout.FormLayoutElement`
class for handling table form layouts.'''

    def __init__(self, form, formset, fields = None, **kwargs):
        self.formset = formset
        self.form_class = form.base_inlines[formset].form_class
        fields = fields or ()
        super(TableRelatedFieldset,self).__init__(fields,**kwargs)
        self.row_maker = TableRow(*self.fields)
        
    def field_heads(self, headers):
        dfields = self.form_class.base_fields
        self.hidden_fields = []
        headers = list(headers)
        for field in dfields:
            if field not in headers:
                headers.append(field)
        for name in headers:
            field = dfields.get(name)
            if field:
                if field.is_hidden:
                    self.hidden_fields.append(name)
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
            row = self.child_widget(self.row_maker, widget, form = form)
            yield row.render(request)
    
    def layout_stream(self, request, widget, context):
        for data in super(TableRelatedFieldset,self).layout_stream(request,\
                                                    widget, context):
            yield data
        formset = widget.form.form_sets[self.formset]
        # Loop over hidden fields
        if self.hidden_fields:
            for form in formset.forms:
                for field in self.hidden_fields:
                     child = self.child_widget(field, widget, form = form)
                     yield child.render(request)
        # the number of forms
        w = formset.num_forms.widget()
        yield w.render(request)
    

