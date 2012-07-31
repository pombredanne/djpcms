import os
import logging
import json

from djpcms import forms, html, Renderer
from djpcms.html import classes, WidgetMaker, panel
from djpcms.utils.text import capfirst, nicename
from djpcms.cms.formutils import form_data_files

_plugin_dictionary = {}
_wrapper_dictionary = {}

CLOSE_DIV = '\n</div>'
PLUGIN_DATA_FORM_CLASS = 'plugin-data-form'


__all__ = ['DJPwrapper', 'DJPplugin']


def ordered_generator(di):
    def _(*args):
        return ((c.name,c.description) for c in sorted(di.values(),\
                                 key=lambda x: x.description))
    return _


plugingenerator  = ordered_generator(_plugin_dictionary)
wrappergenerator = ordered_generator(_wrapper_dictionary)
get_plugin = lambda name, default = None:  _plugin_dictionary.get(name,default)
get_wrapper = lambda name, default = None: _wrapper_dictionary.get(name,default)


def register_application(app, name = None, description = None):
    '''Register an application view as a plugin
* *app* is an instance of an :class:`djpcms.views.appview.AppViewBase`
* *name* name for this plugin'''
    global _plugin_dictionary
    if hasattr(app,'get_plugin'):
        p = app.get_plugin()
    else:
        p = ApplicationPlugin(app)


def html_plugin_form(form):
    if isinstance(form, forms.FormType):
        form = forms.HtmlForm(form)
    if isinstance(form,forms.HtmlForm):
        form.tag = None
    return form


class DJPpluginMetaBase(type):
    '''
    Just a metaclass to differentiate plugins from other calsses
    '''
    def __new__(cls, name, bases, attrs):
        new_class = super(DJPpluginMetaBase, cls).__new__
        if 'form' in attrs:
            attrs['form'] = html_plugin_form(attrs['form'])
        if attrs.pop('virtual',None) or not attrs.pop('auto_register',True):
            return new_class(cls, name, bases, attrs)
        pname = attrs.get('name',None)
        if pname is None:
            pname = name
        pname = pname.lower()
        descr = attrs.get('description')
        if not descr:
            descr = nicename(pname)
        attrs['name'] = pname
        attrs['description'] = descr
        pcls = new_class(cls, name, bases, attrs)
        pcls()._register()
        return pcls


DJPpluginBase = DJPpluginMetaBase('DJPpluginBase',(object,),{'virtual':True})
DJPwrapperBase = DJPpluginMetaBase('DJPwrapperBase',(Renderer,),{'virtual':True})


class DJPwrapper(DJPwrapperBase):
    '''A :class:`djpcms.Renderer` for wrapping
:ref:`djpcms plugins <plugins-index>`.'''
    virtual = True
    template = WidgetMaker(tag='div')
    name = None

    def render(self, request, block, html):
        '''Wrap content for block and return safe HTML.
This function should be implemented by derived classes.

:parameter cblock: instance of :class:'djpcms.core.page.Block`.
:parameter html: safe unicode string of inner HTML.'''
        return html

    def __call__(self, request, block, html):
        el = self.render(request, block, html)
        if self.template:
            el = self.template(el, id=block.htmlid())
        return el.addClass((classes.cms_block, 'plugin-'+block.plugin_name))

    def _register(self):
        global _wrapper_dictionary
        _wrapper_dictionary[self.name] = self


class DJPplugin(DJPpluginBase):
    '''Base class for Plugins. These classes are used to display contents
on a ``djpcms`` powered web site. The basics:

* A Plugin is dynamic application.
* It is rendered within a :class:`DJPwrapper`, and each :class:`DJPwrapper`
  displays a plugin.
* It can define style and javascript to include in the page, in a static way
  (as a ``meta`` property of the class) or in a dynamic way by member functions.
* It can have parameters to control its behavior.

.. attribute:: css_name

    Optional ``name`` which associate this plugin with a css element.
'''

    virtual       = True
    '''If set to true, the class won't be registered with the plugin's dictionary. Default ``False``.'''
    name          = None
    '''Unique name. If not provided the class name will be used. Default ``None``.'''
    description   = None
    '''A short description to display in forms when editing content.'''
    form = None
    '''A :class:`djpcms.forms.Form` class or :class:`djpcms.forms.HtmlForm`
instance for editing the plugin parameters.

Default: ``None``, the plugin has no arguments.'''
    permission = 'authenticated'
    css_name = None

    def js(self, **kwargs):
        '''Function which can be used to inject javascript dynamically.'''
        return None

    def css(self):
        '''Function which can be used to inject css dynamically.'''
        return None

    def for_model(self, request):
        pass

    def arguments(self, args):
        try:
            kwargs = json.loads(args)
            if isinstance(kwargs,dict):
                rargs = {}
                for k,v in kwargs.items():
                    rargs[str(k)] = v
                return self.processargs(rargs)
            else:
                return {}
        except:
            return {}

    def processargs(self, kwargs):
        '''You can use this hook to perform pre-processing on plugin parameters if :attr:`form` is set.
By default do nothing.
        '''
        return kwargs

    def __call__(self, request, args=None, block=None, prefix=None):
        return self.render(request, block, prefix, **self.arguments(args))

    def edit_url(self, request, args = None):
        return None

    def render(self, request, block, prefix, **kwargs):
        '''Render the plugin. It returns a safe string to be included in the
 HTML page. This is the function subclasses need to implement.

:parameter block: instance of a :class:`djpcms.core.page.Block` where
    the plugin is rendered.
:parameter prefix: A prefix string for the block.
:parameter kwargs: plugin specific key-valued arguments.
'''
        return ''

    def save(self, pform):
        '''Save the plugin data from the plugin form'''
        if pform:
            return json.dumps(pform.data)
        else:
            return json.dumps({})

    def get_form(self, request, args=None, prefix=None, **kwargs):
        '''Return an instance of a :attr:`form` or `None`.
Used to edit the plugin when in editing mode.
Usually, there is no need to override this function.
If your plugin needs input parameters when editing, simple set the
:attr:`form` attribute.'''
        form_factory = self.form
        if form_factory is not None:
            initial = self.arguments(args) or None
            method = form_factory.attrs['method']
            data, files, initial = form_data_files(request, initial=initial,
                                                   method=method)
            form = form_factory(request=request,
                                initial=initial,
                                prefix=prefix,
                                model=self.for_model(request),
                                data=data,
                                files=files,
                                **kwargs)
            return form

    def _register(self):
        global _plugin_dictionary
        _plugin_dictionary[self.name] = self

    def __eq__(self, other):
        if isinstance(other,DJPplugin):
            return self.name == other.name
        return False

    def media(self, request):
        return None


class EmptyPlugin(DJPplugin):
    '''
    This is the empty plugin. It render nothing
    '''
    name         = ''
    description  = '--------------------'


class ThisPlugin(DJPplugin):
    '''Current view plugin. This plugin render the current view
only if it is an instance of :class:`djpcms.views.View`.
For example if the current view is a :class:`djpcms.views.SearchView`,
the plugin will display the search view for that application.
    '''
    name        = 'this'
    description = 'Current View'

    def render(self, request, block, prefix, **kwargs):
        return request.render(block=block)


class ApplicationPlugin(DJPplugin):
    '''Plugin formed by :class:`djpcms.views.View` which have
the :attr:`djpcms.views.RendererMixin.has_plugins` attribute
set to ``True``.'''
    auto_register = False

    def __init__(self, view, name=None, description=None):
        global _plugin_dictionary
        self.view = view
        self.form = view.plugin_form
        name = name or view.code
        description = description or view.description or name
        self.name = name
        self.description = nicename(description)
        _plugin_dictionary[self.name] = self

    def render(self, request, block, prefix, **kwargs):
        req = request.for_path(self.view.path)
        if req and req.has_permission():
            return req.render(block=block, **kwargs)
        else:
            return ''


class JavascriptLogger(DJPplugin):
    description = 'Javascript Logging Panel'

    def render(self, request, block, prefix, **kwargs):
        return '<div class="djp-logging-panel"></div>'


class NoWrapper(DJPwrapper):
    name = '             nothing'
    description  = '--------------------'


class FlatPanel(DJPwrapper):
    name = 'panel'
    description = 'Panel'
    def render(self, request, block, content):
        return panel(content)


default_content_wrapper = NoWrapper()
