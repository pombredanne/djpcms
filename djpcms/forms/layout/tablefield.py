from djpcms import html
from djpcms.html import icons
from djpcms.utils.text import nicename

from .table import BaseTableFormElement, TableRow


__all__ = ['TableRelatedFieldset']

    
class TableRelatedFieldset(BaseTableFormElement):
    '''A :class:`djpcms.forms.layout.FormLayoutElement`
class for handling table form layouts.'''
    tag = 'div'
    default_style = 'tablerelated'
    _template_name__ = ('djpcms/form-layouts/tableformset.html',)
    _field_template__ = '''\
{% if hidden %}{{ inner }}{% else %}
<div {% if error %}class="error"{% endif %}>{% if ischeckbox %}
{{ inner }}
{% else %}
<div class="field-widget input ui-widget-content {{ name }}">
{{ inner }}
</div>{% endif %}
</div>{% endif %}'''
    
    def __init__(self, form, formset, fields = None, initial = 3,
                 **kwargs):
        super(TableRelatedFieldset,self).__init__(**kwargs)
        self.initial = initial
        self.formset = formset
        self.form_class = form.base_inlines[formset].form_class
        self.fields = fields or ()
        
    def check_fields(self, missings, layout):
        # Override default
        dfields = self.form_class.base_fields
        nf = list(self.fields)
        for field in dfields:
            if field not in nf:
                nf.append(field)
        self.fields = tuple(nf)
        self.headers = [self.field_head(name,dfields[name])\
                         for name in self.fields]
            
    def render_form_fields(self, request, widget):
        form = widget.form
        dfields = form.dfields
        for head in self.headers:
            w = self.child_widget(head['name'],widget)
            ctx = w.maker.get_context(djp,w,{})
            loader = djp.site.template
            ctx['inner'] = loader.template_class(self.field_template)\
                                    .render(ctx)
            yield ctx
            
        has_delete = self.has_delete
        if has_delete is None or has_delete:
            if form.instance.id:
                deleteurl = djp.site.get_url(form.model,
                                             'delete',
                                             request = djp.request,
                                             instance = form.instance,
                                             all = True)
                if deleteurl:
                    link = ''
                    #link = icons.delete(deleteurl, cn='ajax')\
                    #            .addData('conf','Please confirm you wish to delete {0}'.format(form.instance))\
                    #            .render()
                else:
                    link = ''
            else:
                link = ''
            if has_delete is None:
                if link:
                    has_delete = True
                else:
                    has_delete = False
        if has_delete:
            yield {'inner':link}
            
    def row_generator(self, request, widget):
        formset = widget.form.form_sets[self.formset]
        for form in formset.forms:
            dfields = form.dfields
            row = TableRow(self.headers, form = form)
            w = self.child_widget(head['name'], widget)
            
        if form.instance and form.instance.id:
            form.mapper.unique_id(form.instance)
        
    def render_form(self,djp,form,widget):
        '''Render a single form in the formset'''
        widget = widget.copy(form = form)
        
        ctx = {'fields': list(self.render_form_fields(djp,widget))}
        if form.instance and form.instance.id:
            ctx['id'] = form.mapper.unique_id(form.instance)
        return ctx
    
    def stream(self, request, widget, context):
        for data in super(TableRelatedFieldset,self).stream(request, widget,
                                                            context):
            yield data
        formset = widget.form.form_sets[self.formset]
        yield formset.num_forms.render()
    

