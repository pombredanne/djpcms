from django.utils import safestring
from django.utils import html
from django.template import loader, Context, Template
from django.template import context

from .base import LibraryTemplateHandler


class TemplateHandler(LibraryTemplateHandler):
    TemplateDoesNotExist = loader.TemplateDoesNotExist
    
    def setup(self):
        self.mark_safe = safestring.mark_safe
        self.template_class = Template
        self.context_class = Context
        self.escape = html.escape
        self.conditional_escape = html.conditional_escape
        self.get_processors = context.get_standard_processors
        self.find_template = loader.find_template
        
    def get_template(self, template_name):
        if isinstance(template_name, (list, tuple)):
            return loader.select_template(template_name)
        else:
            return loader.get_template(template_name)

    def loaders(self):
        '''Django sucks, since it does not have a function to return the loaders'''
        if loader.template_source_loaders is None:
            try:
                loader.find_template('')
            except self.TemplateDoesNotExist:
                pass
        return loader.template_source_loaders
    
    def render(self, template_name, dictionary=None, autoescape = False):
        context_instance = Context(dictionary, autoescape = autoescape)
        t = self.get_template(template_name)
        return t.render(context_instance)
    
    def render_from_string(self, template, dictionary=None, autoescape = False):
        context_instance = Context(dictionary, autoescape = autoescape)
        return Template(template).render(context_instance)
    
    def template_variables(self, template_name):
        t = self.get_template(template_name)
        for node in t:
            yield node
        

