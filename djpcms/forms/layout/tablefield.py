from djpcms import html
from djpcms.html import icons
from djpcms.template import loader
from djpcms.utils.text import nicename

from .base import FormLayoutElement, FieldWidget, check_fields


__all__ = ['TableRelatedFieldset']


class TableRelatedFieldset(FormLayoutElement):
    '''A :class:`djpcms.forms.layout.FormLayoutElement`
class for handling formsets as tables.'''
    tag = 'div'
    default_style = 'tablerelated'
    template_name = ('djpcms/form-layouts/tableformset.html',)
    field_template = '''\
{% if is_hidden %}{{ inner }}{% else %}
<div {% if error %}class="error"{% endif %}>{% if ischeckbox %}
{{ inner }}
{% else %}
<div class="field-widget input {{ name }}">
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
        dfields = self.form_class.base_fields
        nf = list(self.fields)
        for field in dfields:
            if field not in nf:
                nf.append(field)
        self.fields = tuple(nf)
        self.headers = [self.field_head(name,dfields[name])\
                         for name in self.fields]
            
    def field_head(self, name, field):
        if field.is_hidden:
            return {'name':name}
        else:
            label = field.label or nicename(name)
            ch = html.Widget('span')
            if field.required:
                ch.addClass('required')
            return {'label': ch.render(inner = label),
                    'name':name,
                    'help_text':field.help_text}
    
    def render_form_fields(self,djp,widget):
        form = widget.form
        dfields = form.dfields
        for head in self.headers:
            w = self.child_widget(head['name'],widget)
            ctx = w.maker.get_context(djp,w,{})
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
            
    def render_form(self,djp,form,widget):
        '''Render a single form in the formset'''
        widget = widget.copy(form = form)
        ctx = {'fields': list(self.render_form_fields(djp,widget))}
        if form.instance and form.instance.id:
            ctx['id'] = form.mapper.unique_id(form.instance)
        return ctx
    
    def get_context(self, djp, widget, keys):
        self.has_delete = None
        formset = widget.form.form_sets[self.formset]
        forms = [self.render_form(djp, form, widget)\
                                   for form in formset.forms]
        if self.has_delete:
            self.headers.append(self.field_head('label','delete'))
        return {'legend': self.legend_html,
                'num_forms': formset.num_forms.render(),
                'headers': self.headers,
                'forms': forms}

