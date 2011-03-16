
def handle(engine = None):
    from djpcms import sites
    engine = engine or sites.settings.TEMPLATE_ENGINE
    if engine not in _handlers:
        handle = get_engine(engine)
        _handlers[engine] = handle
    else:
        handle = _handlers[engine]
    return handle
        
        
def get_engine(engine, config = None):
    from djpcms import sites
    config = config or sites.settings
    if engine == 'django':
        from ._django import TemplateHandler
    elif engine == 'jinja2':
        from ._jinja2 import TemplateHandler
    elif engine == 'cheetah':
        raise NotImplementedError("Cheetah not yet supported.")
    elif engine == 'mustache':
        raise NotImplementedError("Mustache not yet supported.")
    elif not engine:
        raise NotImplementedError('Template handler not specified')
    else:
        raise NotImplementedError('Template handler {0} not available'.format(engine))
    return TemplateHandler(config)


class BaseTemplateHandler(object):
    '''Base class which wraps third-parties template libraries.'''
    TemplateDoesNotExist = None
    
    def setup(self):
        '''Called when the handler is initialized and therefore it is not
relevant for end-user but for developers wanting to add additional libraries.'''
        raise NotImplementedError
    
    def context(self, dictionary=None, request = None, processors=None):
        '''Evaluate the context for the template. It returns a dictionary
which updates the input ``dictionary`` with library dependent information.
        '''
        c = dictionary
        if request:
            info = request.DJPCMS
            if info.context_cache is None:
                info.context_cache = context_cache = {}
                site_processors = info.site.template_context()
                if processors is not None:
                    site_processors += tuple(processors)
                for processor in site_processors:
                    context_cache.update(processor(request))
            c.update(info.context_cache)
        return c
    
    def loaders(self):
        '''List of template loaders for thie library'''
        raise NotImplementedError
    
    def render(self, template_name, dictionary, autoescape=False):
        '''Render a template form a file name:
        
:parameter template_name: template file name.
:parameter dictionary: a dictionary of context variables.
:parameter autoescape: if ``True`` the resulting string will be escaped.'''
        raise NotImplementedError
    
    def render_from_string(self, template_string, dictionary, autoescape = False):
        '''Render a template form a file:

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
    

class TemplateHandler(BaseTemplateHandler):
    
    @property
    def template_class(self):
        return handle().template_class
    
    @property
    def context_class(self):
        return handle().context_class
    
    def escape(self, html):
        return handle().escape(html)
    
    def conditional_escape(self, html):
        return handle().escape(html)
    
    def mark_safe(self, html):
        return handle().mark_safe(html)
    
    def loaders(self):
        return handle().loaders()
    
    def find_template(self, template_name, **dirs):
        '''Returns a tuple containing the source and origin for the given template
        name.'''
        return handle().find_template(template_name, **dirs)
    
    def render(self, template_name, dictionary, autoescape=False):
        return handle().render(template_name,
                               dictionary,
                               autoescape=autoescape)
        
    def render_from_string(self, template_string, dictionary, autoescape=False):
        return handle().render_from_string(template_string,
                                           dictionary,
                                           autoescape=autoescape)
        
    def load_template_source(self, template_name, dirs=None):
        return handle().load_template_source(template_name, dirs)
    
    def template_variables(self, template_name):
        return handle().template_variables(template_name)
    

class LibraryTemplateHandler(BaseTemplateHandler):
    template_class = None
    context_class = None
    
    def __init__(self, config):
        self.config = config
        self.setup()

    def setup(self):
        raise NotImplementedError
            
    def find_template(self, template_name, **dirs):
        raise NotImplementedError
    
    
_handlers = {}
