from djpcms.dispatch import Signal
from djpcms import sites


def handle(engine = None, settings = None):
    engine = engine or 'jinja2'
    if engine not in _handlers:
        handle = get_engine(engine)
        _handlers[engine] = handle
    else:
        handle = _handlers[engine]
    return handle(settings)
    
        
def get_engine(engine):
    if engine == 'django':
        from ._django import TemplateHandler
    elif engine == 'jinja2':
        from ._jinja2 import TemplateHandler
    else:
        raise NotImplementedError('Template handler {0} not available'\
                                  .format(engine))
    return TemplateHandler


class BaseTemplateHandler(object):
    '''Base class which wraps third-parties template libraries.'''
    TemplateDoesNotExist = None
    
    def __init__(self):
        self.context_ready = Signal()
    
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
            ccache = request.DJPCMS.context(request)
            c.update(ccache)
        self.context_ready.send(self, context = c)
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
        super(LibraryTemplateHandler,self).__init__()
        self.config = config
        self.setup()

    def setup(self):
        raise NotImplementedError
            
    def find_template(self, template_name, **dirs):
        raise NotImplementedError
    
    
_handlers = {}
