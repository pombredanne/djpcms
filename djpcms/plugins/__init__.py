import os
import logging
import json

from djpcms import forms, to_string
from djpcms.forms.utils import form_kwargs
from djpcms.utils import force_str
from djpcms.utils.text import capfirst, nicename

_plugin_dictionary = {}
_wrapper_dictionary = {}

CLOSE_DIV = '\n</div>'


def ordered_generator(di):
    def _(*args):
        return ((c.name,c.description) for c in sorted(di.values(), key=lambda x: x.description))
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


class DJPpluginMetaBase(type):
    '''
    Just a metaclass to differentiate plugins from other calsses
    '''
    def __new__(cls, name, bases, attrs):
        new_class = super(DJPpluginMetaBase, cls).__new__
        if attrs.pop('virtual',None) or not attrs.pop('auto_register',True):
            return new_class(cls, name, bases, attrs)
        pname = attrs.get('name',None)
        if pname is None:
            pname = name
        pname = pname.lower()
        descr = attrs.get('description',None)
        if not descr:
            descr = pname
        if pname != '':
            descr = nicename(descr) 
        attrs['name'] = pname
        attrs['description'] = descr
        pcls = new_class(cls, name, bases, attrs)
        pcls()._register()
        return pcls


DJPpluginBase = DJPpluginMetaBase('DJPpluginBase',(object,),{'virtual':True})
DJPwrapperBase = DJPpluginMetaBase('DJPwrapperBase',(object,),{'virtual':True})


class DJPwrapper(DJPwrapperBase):
    '''Class responsible for wrapping :ref:`djpcms plugins <plugins-index>`.
    '''
    virtual       = True
    
    name          = None
    '''Unique name. If not provided the class name will be used.
    
    Default ``None``.'''
    form_layout   = None
    
    _head_template = to_string('<div id="{0}"\
 class="djpcms-block-element plugin-{1}">\n')
    _wrap_template = to_string('{0}{1}\n</div>')

    def wrap(self, djp, cblock, html):
        '''Wrap content for block and return safe HTML.
This function should be implemented by derived classes.
        
* *djp* instance of :class:`djpcms.views.response.DjpResponse`.
* *cblock* instance of :class:'djpcms.models.BlockContent`.
* *html* safe unicode string of inner HTML.'''
        return html if html else ''
    
    def __call__(self, djp, cblock, html):
        name  = cblock.plugin_name
        id    = cblock.htmlid()
        head  = self._head_template.format(id,name)
        inner = self.wrap(djp, cblock, html)
        return self._wrap_template.format(head,inner)
    
    def _register(self):
        global _wrapper_dictionary
        _wrapper_dictionary[self.name] = self
        
    def media(self):
        return None


class DJPplugin(DJPpluginBase):
    '''Base class for Plugins. These classes are used to display contents on a ``djpcms`` powered site.
The basics:
    
* A Plugin is dynamic application.
* It is rendered within a :class:`DJPwrapper` and each :class:`DJPwrapper` displays a plugin.
* It can define style and javascript to include in the page, in a static way (as a ``meta`` property of the class) or in a dynamic way by member functions.
* It can have parameters to control its behaviour.'''
    
    virtual       = True
    '''If set to true, the class won't be registered with the plugin's dictionary. Default ``False``.'''
    name          = None
    '''Unique name. If not provided the class name will be used. Default ``None``.'''
    description   = None
    '''A short description to display in forms.'''
    form          = None
    '''Form class for editing the plugin parameters. Default ``None``, the plugin has no arguments.'''
    permission      = 'authenticated'
    #storage       = _plugin_dictionary
    #URL           = None
    for_model = None
    
    def js(self, **kwargs):
        '''Function which can be used to inject javascript dynamically.'''
        return None
    
    def css(self):
        '''Function which can be used to inject css dynamically.'''
        return None
    
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
    
    def __call__(self, djp, args = None, block = None, prefix = None):
        djp.block = block
        return self.render(djp, block, prefix, **self.arguments(args))
        
    def edit_url(self, djp, args = None):
        return None
    
    def render(self, djp, block, prefix, **kwargs):
        '''Render the plugin. It returns a safe string to be included in the
 HTML page. This is the function subclasses need to implement.

:parameter djp: instance of :class:`djpcms.views.response.DjpResponse`.
:parameter block: instance of a :class:`djpcms.Block` where the plugin is
    rendered.
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
    
    def get_form(self, djp, args = None, prefix = None, **kwargs):
        '''Return an instance of a :attr:`form` or `None`. Used to edit the plugin when
in editing mode. Usually, there is no need to override this function.
If your plugin needs input parameters when editing, simple set the
:attr:`form` attribute.'''
        form_class = self.form
        if form_class:
            if isinstance(form_class,forms.FormType):
                form_class = forms.HtmlForm(form_class)
            form_class.tag = None
            initial = self.arguments(args) or None
            form =  form_class(**form_kwargs(request = djp.request,
                                             initial = initial,
                                             prefix = prefix,
                                             model = self.for_model))
            return form
        #form_class.widget(form, **kwargs)
    
    def _register(self):
        global _plugin_dictionary
        _plugin_dictionary[self.name] = self
        
    def __eq__(self, other):
        if isinstance(other,DJPplugin):
            return self.name == other.name
        return False
    
    def media(self):
        return None
    

class EmptyPlugin(DJPplugin):
    '''
    This is the empty plugin. It render nothing
    '''
    name         = ''
    description  = '--------------------'
    

class ThisPlugin(DJPplugin):
    '''Current view plugin. This plugin render the current view
only if it is an instance of :class:`djpcms.views.appview.AppViewBase`.
For example if the current view is a :class:`djpcms.views.appview.SearchView`,
the plugin will display the search view for that application.
    '''
    name        = 'this'
    description = 'Current View'
    
    def render(self, djp, block, prefix, **kwargs):
        djp.block = block
        return djp.render()
    
    
class ApplicationPlugin(DJPplugin):
    '''Plugin formed by :class:`djpcms.views.appview.AppViewBase` classes
which have the :attr:`djpcms.views.appview.AppViewBase.isplugin` attribute
set to ``True``.

For example, lets say an application as a :class:`djpcms.views.appview.AddView` view
which is registered to be a plugin, than it will be managed by this plugin.'''
    auto_register = False
    
    def __init__(self, app, name = None, description = None):
        global _plugin_dictionary
        self.app  = app
        self.form = app.plugin_form
        if not name:
            name = '%s-%s' % (app.appmodel.name,app.name)
        if not description:
            description = app.description or name
        self.name = name
        self.description = nicename(description)
        _plugin_dictionary[self.name] = self
        
    def render(self, djp, block, prefix, **kwargs):
        app  = self.app
        request = djp.request
        if app.has_permission(request):
            if djp.view != app or kwargs:
                args = djp.kwargs.copy()
                args.update(kwargs)
                djp = app(djp.request, **args)
            djp.block = block
            return djp.render()
        else:
            return ''
    
    def media(self):
        return self.app.media()
    

class JavascriptLogger(DJPplugin):
    description = 'Javascript Logging Panel'
    
    def render(self, djp, block, prefix, **kwargs):
        return '<div class="djp-logging-panel"></div>'
    
    
class SimpleWrap(DJPwrapper):
    name         = 'simple no-tags'

default_content_wrapper = SimpleWrap()
