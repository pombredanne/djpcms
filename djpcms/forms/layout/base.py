from inspect import isclass

from djpcms import html, ajax
from djpcms.utils.text import nicename


__all__ = ['FormWidget',
           'BaseFormLayout',
           'FormLayout',
           'FormLayoutElement',
           'DivFormElement',
           'nolabel',
           'TableRelatedFieldset']


nolabel = 'nolabel'


class FormElementWidget(html.Widget):
    '''A :class:`djpcms.html.HtmlWidget` used to display
forms using the :mod:`djpcms.forms.layout` API.'''
    def __init__(self, maker, form, layout):
        super(FormWidget,self).__init__(maker)
        self.form = form
        self.layout = layout
    

class BaseFormLayout(html.WidgetMaker):
    '''\
A :class:`djpcms.html.HtmlWidgetMaker` for programmatic
form layout design.
    
.. attribute:: field_template

    A template name or tuple for rendering a bound field. If not provided
    the field will render the widget only.
    
    Default: ``None``.
'''
    field_template = None
    required_tag = ''
    
    def __init__(self, required_tag = None,
                 field_template = None, legend = None,
                 **params):
        self.required_tag = required_tag or self.required_tag
        if legend:
            legend = '{0}'.format(legend)
        else:
            legend = ''
        self.legend_html = legend
        super(BaseFormLayout,self).__init__(**params)


def check_fields(fields, missings):
    for field in fields:
        if field in missings:
            missings.discard(field)
        else:
            field.check_fields(missings)


class FormLayoutElement(BaseFormLayout):
    '''A :class:`djpcms.forms.layout.BaseFormLayout` 
class for a :class:`djpcms.forms.layout.FormLayout` element.
It defines how form fields are rendered and it can
be used to add extra html elements to the form.
'''
    def check_fields(self, missings):
        raise NotImplementedError
    
    def render_field(self, djp, bfield, layout):
        '''\
Render a single bound field using a layout.

:parameter djp: instance of :class:`djpcms.views.DjpResponse`.
:parameter bfield: instance of :class:`djpcms.forms.BoundField` to render.
:parameter layout: the instance of :class:`djpcms.forms.layout.FormLayout`
                   to which ``self`` belongs to.

It uses the :attr:`djpcms.forms.layout.BaseFormLayout.field_template`
attribute to render the bounded field.
        '''
        form = bfield.form
        name = bfield.name
        rendered_fields = layout.get_rendered_fields(form)
        if not bfield.name in rendered_fields:
            rendered_fields[bfield.name] = bfield
        else:
            raise Exception("A field should only be rendered once: %s" % bfield)
        widget = bfield.field.get_widget(djp, bfield)
        self.add_widget_classes(bfield,widget)
        field_template = self.field_template or layout.field_template
        whtml = widget.render(djp, bfield)
        if not field_template:
            return whtml
        else:
            ctx = {'label': None if self.default_style == nolabel else bfield.label,
                   'name': name,
                   'required_tag': self.required_tag or layout.required_tag,
                   'field':bfield,
                   'error': form.errors.get(name,''), 
                   'widget':whtml,
                   'is_hidden': widget.is_hidden,
                   'ischeckbox':widget.ischeckbox()}
            return loader.render(field_template,ctx)

    def add_widget_classes(self, field, widget):
        pass
    

class DivFormElement(FormLayoutElement):
    
    def __init__(self, *fields, **kwargs):
        super(DivFormElement,self).__init__(**kwargs)
        self.fields = fields

    def check_fields(self, missings):
        check_fields(self.fields,missings)
        
    def _innergen(self, djp, form, layout):
        attr = self.flatatt()
        dfields = form.dfields
        for field in self.fields:
            yield '<div{0}>'.format(attr)
            yield self.render_field(djp,dfields[field],layout)
            yield '</div>'
            
    def inner(self, djp, form, layout):
        return '\n'.join(self._innergen(djp, form, layout))
    

class Inputs(FormLayoutElement):
    template = 'djpcms/form-layouts/inputs.html'
    
    def render(self, djp, form, layout):
        inputs = form._inputs
        if inputs:
            form._inputs = None
            ctx = {'has_inputs': len(inputs),
                   'style': self.default_style or layout.default_style,
                   'inputs': (input.render(djp) for input in inputs)}
            return loader.render(self.template, ctx)
    

class FormLayout(BaseFormLayout):
    '''Base form class for form layout design'''
    
    '''Form template'''
    '''Template file for rendering form fields'''
    form_class = None
    '''form css class'''
    form_messages_container_class = 'form-messages'
    '''Class used to hold form-wide messages'''
    form_error_class = 'errorlist ui-state-error'
    '''Class for form errors'''
    form_message_class = 'messagelist ui-state-highlight'
    '''Class for form messages'''
    default_element = DivFormElement
    
    def __init__(self, *fields, **kwargs):
        super(FormLayout,self).__init__(**kwargs)
        self.add(*fields)
        
    def check_fields(self, missings):
        '''Add missing fields to ``self``. This
method is called by the Form widget factory :class:`djpcms.forms.HtmlForm`.

:parameter form: a :class:`djpcms.forms.Form` class.
'''
        for field in self.allchildren:
            if isinstance(field,FormLayoutElement):
                field.check_fields(missings)
        if missings:
            self.add(self.default_element(*missings))
        
    def render(self, djp, form, inputs, **keys):
        ctx  = {'layout':self}
        html = ''
        template = self.template
        form._inputs = inputs
        for field in self.allchildren:
            w = field.widget(form, self)
            key = field.key
            if key and key in keys:
                html += w.render(djp, keys[key])
            else:
                h = w.render(djp)
                if key and template:
                    ctx[field.key] = h
                else:
                    html += h
        if form._inputs:
            ctx['inputs'] = Inputs().render(djp,form,self)
        ctx['form']   = html
        ctx['messages'] = ''
        return loader.render(template, ctx)

    def json_messages(self, f):
        '''Convert errors in form into a JSON serializable dictionary with keys
        given by errors html id.'''
        dfields = f._fields_dict
        ListDict = jhtmls()
        self._add(ListDict,dfields,f.errors,self.form_error_class)
        self._add(ListDict,dfields,f.messages,self.form_message_class)
        for fset in f.form_sets.values():
            for f in fset.forms:
                dfields = f._fields_dict
                self._add(ListDict,dfields,f.errors,self.form_error_class)
                self._add(ListDict,dfields,f.messages,self.form_message_class)
        return ListDict
        
    def _add(self, ListDict, fields, container, msg_class):
        # Add messages to the list dictionary
        for name,msg in container.items():
            if name in fields:
                name = '#' + fields[name].errors_id
            else:
                name = '.' + self.form_messages_container_class
            ListDict.add(name,
                         List(data = msg, cn = msg_class).render(),
                         alldocument = False)


class TableRelatedFieldset(FormLayoutElement):
    default_style = 'tablerelated'
    
    field_template = ('djpcms/form-layouts/tablefield.html',)
    template = ('djpcms/form-layouts/tableformset.html',)
    
    def __init__(self, formset, fields = None, initial = 3,
                 **kwargs):
        super(TableRelatedFieldset,self).__init__(**kwargs)
        self.initial = initial
        self.formset = formset
        self.fields = fields or ()
    
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
        
        