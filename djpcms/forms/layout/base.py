from inspect import isclass

from djpcms.html import List, HtmlWrap, icons
from djpcms.forms.html import HtmlWidget
from djpcms.template import loader
from djpcms.utils.ajax import jhtmls
from djpcms.utils.text import nicename

__all__ = ['BaseFormLayout',
           'FormLayout',
           'FormLayoutElement',
           'DivFormElement',
           'Html',
           'nolabel',
           'TableRelatedFieldset']


nolabel = 'nolabel'


class BaseFormLayout(HtmlWidget):
    '''\
A :class:`djpcms.html.HtmlWidget` base class for programmatic
form layout design.
    
.. attribute:: field_template

    A template name or tuple for rendering a bound field. If not provided
    the field will render the widget only.
    
    Default: ``None``.
'''
    field_template = None
    default_style = None
    required_tag = ''
    
    def __init__(self, default_style = None, required_tag = None,
                 field_template = None, legend = None,
                 **kwargs):
        self.default_style = default_style or self.default_style
        self.required_tag = required_tag or self.required_tag
        if legend:
            legend = '{0}'.format(legend)
        else:
            legend = ''
        self.legend_html = legend
        super(BaseFormLayout,self).__init__(**kwargs)



class FormLayoutElement(BaseFormLayout):
    '''A :class:`djpcms.forms.layout.BaseFormLayout` 
class for a :class:`djpcms.forms.layout.FormLayout` element.
It defines how form fields are rendered and it can
be used to add extra html elements to the form.

:parameter key: An optional string. It is used to easily retrieve the
                element in the layout which holds it.
                If specified, the element
                will be an attribute named ``key`` of the layout itself.
                
                Default: ``None``
                
:parameter elem_css: defining element class name.
:parameter kwargs: additional parameters to be passed to the
                   :class:`djpcms.forms.layout.BaseFormLayout` base class.
'''
    elem_css = None
    template = None
    
    def __init__(self, key = None, elem_css = None, **kwargs):
        super(FormLayoutElement,self).__init__(**kwargs)
        self.key = key
        self.elem_css = elem_css or self.elem_css
        
    def make_classes(self):
        self.addClass(self.elem_css).addClass(self.default_style)
        
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


class Html(FormLayoutElement):
    '''A :class:`FormLayoutElement` which renders to `self`.'''
    def __init__(self, html = '', renderer = None, **kwargs):
        super(Html,self).__init__(**kwargs)
        self.html = html

    def inner(self, *args, **kwargs):
        return self.html
    

class DivFormElement(FormLayoutElement):
    
    def __init__(self, *fields, **kwargs):
        super(DivFormElement,self).__init__(**kwargs)
        self.fields = fields

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
        self._allfields = []
        self.add(*fields)
        
    def render(self, djp, form, inputs, **keys):
        ctx  = {'layout':self}
        html = ''
        template = self.template
        form._inputs = inputs
        for field in self._allfields:
            key = field.key
            if key and key in keys:
                html += field.render(djp, form, self, inner = keys[key])
            else:
                h = field.render(djp, form, self)
                if key and template:
                    ctx[field.key] = h
                else:
                    html += h
        
        missing_fields = self.get_missing_fields(form)        
        if missing_fields:
            fset  = self.default_element(*missing_fields).addClass(self.default_style)
            html += fset.render(djp,form,self)
        
        if form._inputs:
            ctx['inputs'] = Inputs().render(djp,form,self)
        ctx['form']   = html
        ctx['messages'] = ''
        
        return loader.render(template, ctx)
        
    def add(self,*fields):
        '''Add *fields* to all fields.
A field must be an instance of :class:`djpcms.forms.layout.FormLayoutElement`.'''
        for field in fields:
            if isinstance(field,FormLayoutElement):
                if not field.default_style:
                    field.default_style = self.default_style
                field.make_classes()
                self._allfields.append(field)
                if field.key:
                    setattr(self,field.key,field)
    
    def get_rendered_fields(self,form):
        rf = getattr(form, '_rendered_fields', {})
        form._rendered_fields = rf
        return rf
    
    def get_missing_fields(self,form):
        mf = []
        rendered_fields = self.get_rendered_fields(form)
        for field in form.fields:
            if not field.name in rendered_fields:
                mf.append(field.name)
        return mf

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
        
        