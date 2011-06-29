from djpcms import html
from djpcms.template import loader
from djpcms.utils.text import nicename

from .base import FormLayoutElement, check_fields


__all__ = ['TableRelatedFieldset']


class TableRelatedFieldset(FormLayoutElement):
    '''A :class:`djpcms.forms.layout.FormLayoutElement`
class for handling formsets as tables.'''
    default_style = 'tablerelated'
    field_template = loader.template_class('''\
{% if is_hidden %}{{ widget }}{% else %}
<div {% if error %}class="error"{% endif %}>{% if ischeckbox %}
    {{ widget }}
    {% else %}
    <div class="field-widget input {{ name }}">
     {{ widget }}
    </div>{% endif %}
</div>{% endif %}''')
    tag = 'div'
    template = None
    template_name = ('djpcms/form-layouts/tableformset.html',)
    
    def __init__(self, form, formset, fields = None, initial = 3,
                 **kwargs):
        super(TableRelatedFieldset,self).__init__(**kwargs)
        self.initial = initial
        self.formset = formset
        self.form_class = form.base_inlines[formset].form_class
        self.fields = fields or ()
        
    def check_fields(self, missings):
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
        
    def render_form_fields(self,djp,form,layout):
        dfields = form.dfields
        for head in self.headers:
            field = dfields[head['name']]
            errors = form.errors.get(field.name,'')
            yield {'html':self.render_form_field(djp, field, layout),
                   'is_hidden':field.is_hidden,
                   'errors':errors,
                   'errors_id':field.errors_id}
        has_delete = self.has_delete
        if has_delete is None or has_delete:
            if form.instance.id:
                deleteurl = djp.site.get_url(form.model,
                                             'delete',
                                             request = djp.request,
                                             instance = form.instance,
                                             all = True)
                if deleteurl:
                    link = icons.delete(deleteurl, cn='ajax')\
                                .addData('conf','Please confirm you wish to delete {0}'.format(form.instance))\
                                .render()
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
            yield {'html':link}
            
    def render_form(self,djp,form,layout):
        '''Render a single form'''
        ctx = {'fields': list(self.render_form_fields(djp,form,layout))}
        if form.instance and form.instance.id:
            ctx['id'] = form.mapper.unique_id(form.instance)
        return ctx
    
    def get_context(self, djp, widget, keys):
        self.has_delete = None
        layout = widget.internal['layout']
        form = widget.internal['form']
        formset = form.form_sets[self.formset]
        forms = [self.render_form(djp, form, layout)\
                  for form in formset.forms]
        if self.has_delete:
            headers.append({'label':'delet'})
        return {'legend': self.legend_html,
                'num_forms': formset.num_forms.render(),
                'headers': self.headers,
                'forms': forms}

