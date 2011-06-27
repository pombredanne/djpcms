from djpcms.template import loader

from .base import FormLayoutElement, check_fields



class TableRelatedFieldset(FormLayoutElement):
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
    
    def __init__(self, formset, fields = None, initial = 3,
                 **kwargs):
        super(TableRelatedFieldset,self).__init__(**kwargs)
        self.initial = initial
        self.formset = formset
        self.fields = fields or ()
        
    def check_fields(self, missings):
        check_fields(self.fields,missings)
    
    def get_formset(self, form):
        return form.form_sets[self.formset]
        
    def headers(self, form):
        formset = self.get_formset(form)
        form_class = formset.form_class
        dfields = form_class.base_fields.copy()
        for name in self.fields:
            field = dfields.pop(name)
            yield self.field_head(name, field)
        for name,field in dfields.items():
            yield self.field_head(name, field)
            
    def field_head(self, name, field):
        if field.is_hidden:
            return {'name':name}
        else:
            label = field.label or nicename(name)
            ch = HtmlWrap('span',inner = label)
            if field.required:
                ch.addClass('required')
            return {'label': ch.render(),
                    'name':name,
                    'help_text':field.help_text}
        
    def render_form_fields(self,djp,form,layout,headers):
        dfields = form.dfields
        for head in headers:
            field = dfields[head['name']]
            errors = form.errors.get(field.name,'')
            yield {'html':self.render_field(djp, field, layout),
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
            
    def render_form(self,djp,form,layout,headers):
        '''Render a single form'''
        ctx = {'fields': list(self.render_form_fields(djp,form,layout,headers))}
        if form.instance.id:
            ctx['id'] = form.mapper.unique_id(form.instance)
        return ctx
    
    def get_context(self, djp, widget, keys):
        pass
    
    def render(self, djp, form, layout, inner = None):
        self.has_delete = None
        headers = list(self.headers(form))
        formset = self.get_formset(form)
        forms = [self.render_form(djp, form, layout, headers) for form in formset.forms]
        if self.has_delete:
            headers.append({'label':'delet'})
        ctx = {'legend': self.legend_html,
               'num_forms': formset.num_forms.render(),
               'headers': headers,
               'self': self,
               'forms': forms}        
        return loader.render(self.template,
                             ctx)    