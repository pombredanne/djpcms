import os
from functools import partial

from djpcms import DJPCMS_DIR


__all__ = ['template_handle', 'ContextTemplate', 'TemplateHandler']


def template_handle(engine, settings = None):
    '''Return an instance of a :class:`TemplateHandler`.'''
    engine = engine.lower()
    if engine not in _handlers and engine == 'jinja2':
        #jinja2 is special, it is our default template library
        import djpcms.apps.jinja2template
    try:
        handle = _handlers[engine]
    except KeyError:
        raise KeyError('Template engine "{0}" not registered'\
                           .format(engine))
    else:
        return handle(settings)


def make_default_inners(sites):
    '''Default inner templates are located in the djpcms/templates/djpcms/inner
 directory'''
    from djpcms.core import orms
    Page = sites.Page
    if not Page:
        raise ValueError('No cms models defined. Cannot create iner templates')
    template = sites.all()[0].template
    template_model = Page.template_model
    mp = orms.mapper(template_model)
    inner_dirs = [(os.path.join(DJPCMS_DIR,'templates','djpcms','inner'),
                   'djpcms/inner/')]
    for dir in sites.settings.TEMPLATE_DIRS:
        inner_dir = os.path.join(dir,'inner')
        if os.path.isdir(inner_dir):
            inner_dirs.append((inner_dir,'inner/'))
    load = template.load_template_source
    added = []
    for inner_dir, relpath in inner_dirs:
        for d in os.listdir(inner_dir):
            if os.path.isfile(os.path.join(inner_dir,d)):
                t,l = load(relpath+d)
                name = d.split('.')[0]
                try:
                    mp.get(name = name)
                except mp.DoesNotExist:
                    it = template_model(name = name, template = t)
                    it.save()
                    added.append(it.name)
    return added


class ContextTemplate(object):
    
    def __init__(self, site):
        self.site = site
        self._engine = template_handle(site.settings.TEMPLATE_ENGINE,
                                       site.settings)
    
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
        data = self.context(data, request, processors)
        if data:
            rc = partial(self._render_context, func, template, **kwargs)
            return self.site.root.render_response(data, rc)
        else:
            return self._render_context(func, template, data, **kwargs)
        
    def context(self, data, request = None, processors=None):
        '''Evaluate the context for the template. It returns a dictionary
which updates the input ``dictionary`` with library dependent information.
        '''
        data = data or {}
        if request:
            environ = request.environ
            if 'djpcms_context' not in environ:
                context_cache = {}
                processors = self.site.template_context
                if processors is not None:
                    for processor in processors:
                        context_cache.update(processor(request))
                environ['djpcms_context'] = context_cache
            data.update(environ['djpcms_context'])
        return data
        
    def _render_context(self, func, template, context, autoescape = None,
                        encode = None, encode_errors = None, **kwargs):
        text = func(template, context, autoescape = autoescape)
        if encode:
            text = text.encode(encode,encode_errors)
        return text


class TemplateHandlerMetaClass(type):
    
    def __new__(cls, name, bases, attrs):
        engine_name = attrs.get('name')
        new_class = super(TemplateHandlerMetaClass, cls)\
                        .__new__(cls, name, bases, attrs)
        if engine_name:
            _handlers[engine_name.lower()] = new_class
        return new_class


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
        '''List of template loaders for thie library'''
        raise NotImplementedError
    
    def render(self, template_name, dictionary, autoescape=False):
        '''Render a template form a file name:
        
:parameter template_name: template file name.
:parameter dictionary: a dictionary of context variables.
:parameter autoescape: if ``True`` the resulting string will be escaped.'''
        raise NotImplementedError
    
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
        

_handlers = {}
