import os
from functools import partial

from djpcms.html.layout import LayoutDoesNotExist, page, get_layout


__all__ = ['template_handle', 'ContextTemplate', 'TemplateHandler']


def template_handle(engine, settings = None):
    '''Return an instance of a :class:`TemplateHandler`.'''
    engine = (engine or 'djpcms').lower()
    if engine not in _handlers and engine == 'jinja2':
        #try to import jinja2 binding. This will fail if jinja2 is not installed
        import djpcms.apps.jinja2template
    try:
        handle = _handlers[engine]
    except KeyError:
        raise KeyError('Template engine "{0}" not registered'\
                           .format(engine))
    else:
        return handle(settings)


class ContextTemplate(object):
    
    def __init__(self, site):
        self.site = site
        engine = site.settings.TEMPLATE_ENGINE
        self._engine = template_handle(engine, site.settings)
    
    @property
    def engine(self):
        '''Instance of a template engine'''
        return self._engine
    
    @property
    def template_class(self):
        '''Template class used by the template :attr:`engine`'''
        return self._engine.template_class
    
    def render(self, template_name, data = None, **kwargs):
        '''render a template file'''
        return self._render(self._engine.render, template_name, data, **kwargs)
        
    def render_from_string(self, template_string, data = None, **kwargs):
        '''render a template string'''
        return self._render(self._engine.render_from_string, template_string,
                            data, **kwargs)
    
    def _render(self, func, template, data, request = None, processors = None,
                **kwargs):
        data = self.site.context(data, request, processors)
        if data:
            rc = partial(self._render_context, func, template, **kwargs)
            return self.site.response(data, callback = rc)
        else:
            return self._render_context(func, template, data, **kwargs)
        
    def _render_context(self, func, template, context, autoescape = None,
                        encode = None, encode_errors = None, **kwargs):
        text = func(template, context, autoescape = autoescape)
        if encode:
            text = text.encode(encode,encode_errors)
        return text

################################################################################
##    Template handlers
################################################################################
class TemplateHandlerMetaClass(type):
    
    def __new__(cls, name, bases, attrs):
        engine_name = attrs.get('name')
        new_class = super(TemplateHandlerMetaClass, cls)\
                        .__new__(cls, name, bases, attrs)
        if engine_name:
            _handlers[engine_name.lower()] = new_class
        return new_class

_handlers = {}
# Needed for Python 2 and python 3 compatibility
TemplateHandlerBase = TemplateHandlerMetaClass('TemplateHandlerBase',\
                                               (object,), {})
    
    
class TemplateHandler(TemplateHandlerBase):
    '''Base class which wraps third-parties template libraries.'''
    name = None
    TemplateDoesNotExist = None
    template_class = None
    
    def __init__(self, config):
        self.config = config
        self.setup()

    def setup(self):
        raise NotImplementedError
            
    def find_template(self, template_name, **dirs):
        raise NotImplementedError
    
    def setup(self):
        '''Called when the handler is initialized and therefore it is not
relevant for end-user but for developers wanting to add additional libraries.'''
        raise NotImplementedError
    
    def loaders(self):
        '''List of template loaders for the library'''
        raise NotImplementedError
    
    def render(self, template_name, dictionary, autoescape=False):
        '''Render a template form a file name:
        
:parameter template_name: template file name.
:parameter dictionary: a dictionary of context variables.
:parameter autoescape: if ``True`` the resulting string will be escaped.'''
        raise NotImplementedError()
    
    def render_from_string(self, template_string, dictionary,
                           autoescape = False):
        '''Render a template form a string:

:parameter template_string: a string defining the template to render.
:parameter dictionary: a dictionary of context variables.
:parameter autoescape: if ``True`` the resulting string will be escaped.'''
        raise NotImplementedError
    
    def template_variables(self, template_name):
        '''Return an iterable over the template variables'''
        raise NotImplementedError
    
    def load_template_source(self, template_name, dirs=None):
        '''Load the template source and return a tuple containing the
        template content as string and the template location'''
        for loader in self.loaders():
            try:
                return loader.load_template_source(template_name, dirs)
            except self.TemplateDoesNotExist:
                pass
        raise self.TemplateDoesNotExist            
        

class djpcms_page_renderer(TemplateHandler):
    '''Default template handler'''
    name = 'djpcms'
    TemplateDoesNotExist = LayoutDoesNotExist
    template_class = page
    
    def setup(self):
        pass
    
    def render(self, template_name, dictionary, autoescape=False):
        if isinstance(template_name, (list, tuple)):
            layout = self.select_layout(template_name)
        else:
            layout = get_layout(template_name)
        request = dictionary.get('request')
        return layout().render(request, context = dictionary)
        
    def render_from_string(self, template_string, dictionary,
                           autoescape = False):
        return self.render(template_string, dictionary, autoescape)
    
    def select_layout(self, template_name_list):
        for template_name in template_name_list:
            try:
                return get_layout(template_name)
            except LayoutDoesNotExist:
                continue
        # If we get here, none of the templates could be loaded
        raise LayoutDoesNotExist(', '.join(template_name_list))
    