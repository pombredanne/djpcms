from djpcms import sites


def handle(engine = None):
    engine = engine or sites.settings.TEMPLATE_ENGINE
    if engine not in _handlers:
        handle = get_engine(engine)
        _handlers[engine] = handle
    else:
        handle = _handlers[engine]
    return handle
        
        
def get_engine(engine, config = None):
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
    '''Base class for template handlers'''
    TemplateDoesNotExist = None
    
    def setup(self):
        raise NotImplementedError
    
    def context(self,
                dict=None, request = None,
                processors=None, current_app=None,
                autoescape=False):
        c = self.context_class(dict, current_app=current_app, autoescape=autoescape)
        if request:
            if hasattr(request,'_context_cache'):
                c.update(request._context_cache)
            else:
                request._context_cache = context_cache = {}
                site_processors = request.site.template_context()
                if processors is not None:
                    site_processors += tuple(processors)
                for processor in site_processors:
                    context_cache.update(processor(request))
            c.update(request._context_cache)
        return c
    
    def loaders(self):
        '''List of template loaders for thie library'''
        raise NotImplementedError
    
    def render(self, template_name, dictionary, autoescape=False):
        '''Render a template name'''
        raise NotImplementedError
    
    def template_variables(self, template_name):
        '''Return an iterable over the template variables'''
        raise NotImplementedError
    
    def load_template_source(self, template_name, dirs=None):
        '''Load the template source and return a tuple containing the
        template content and the template location'''
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
        
    #def render_to_string(self, template_name, dictionary=None, context_instance=None):
    #    return handle().render_to_string(template_name,
    #                                     dictionary=dictionary,
    #                                     context_instance=context_instance)
        
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
