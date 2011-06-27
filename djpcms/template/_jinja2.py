import os

import jinja2

from djpcms import sites
from djpcms.utils.importer import import_module
from djpcms.core.exceptions import ImproperlyConfigured

from .base import LibraryTemplateHandler


TemplateNotFound = jinja2.TemplateNotFound
Template = jinja2.Template


def application_directories(package_path):
    app_template_dirs = []
    if sites.settings:
        for app in sites.settings.INSTALLED_APPS:
            try:
                mod = import_module(app)
            except ImportError as e:
                raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))
            template_dir = os.path.join(os.path.dirname(mod.__file__), package_path)
            if os.path.isdir(template_dir):
                app_template_dirs.append(template_dir)
    return app_template_dirs



class ApplicationLoader(jinja2.loaders.FileSystemLoader):
    
    def __init__(self, package_path='templates', encoding='utf-8'):
        searchpath = application_directories(package_path)
        for path in sites.settings.TEMPLATE_DIRS:
            if path not in searchpath:
                searchpath.append(path)
        super(ApplicationLoader,self).__init__(searchpath,encoding)



AUTOESCAPE_EXTENSION = ('html', 'htm', 'xml')

def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in AUTOESCAPE_EXTENSION


class TemplateHandler(LibraryTemplateHandler):
    
    def setup(self):
        self.template_class = Template
        self.mark_safe = jinja2.Markup
        self.escape = jinja2.escape
        self.conditional_escape = jinja2.escape
        envs = []
        self.envs = envs
        if self.config:
            for elem in self.config.JINJA2_TEMPLATE_LOADERS:
                code, args = elem[0], elem[1:]
                loader = self.find_template_loader(code,args)
                env = jinja2.Environment(loader=loader)
                envs.append(env)
    
    def context_class(self, dict, autoescape=False, **kwargs):
        return dict
    
    def loaders(self):
        return (env.loader for env in self.envs)
        
    def render(self, template_name, data=None, autoescape=False):
        """
        Loads the given template_name and renders it with the given dictionary as
        context. The template_name may be a string to load a single template using
        get_template, or it may be a tuple to use select_template to find one of
        the templates in the list. Returns a string.
        """
        if isinstance(template_name, (list, tuple)):
            t = self.select_template(template_name)
        else:
            t = self.get_template(template_name)
        t.environment.autoescape = autoescape
        if data:
            return t.render(data)
        else:
            return t.render()
    
    def render_from_string(self, template, dictionary=None, autoescape = False):
        t = Template(template)
        t.environment.autoescape = autoescape
        return t.render(dictionary)
    
    def get_template(self, template_name):
        for env in self.envs:
            try:
                return env.get_template(template_name)
            except TemplateNotFound:
                pass
        raise TemplateNotFound(template_name)
    
    def select_template(self, template_name_list):
        "Given a list of template names, returns the first that can be loaded."
        for template_name in template_name_list:
            try:
                return self.get_template(template_name)
            except TemplateNotFound:
                continue
        # If we get here, none of the templates could be loaded
        raise TemplateNotFound(', '.join(template_name_list))
    
    def find_template_loader(self, code, args):
        bits = code.split('.')
        module, attr = '.'.join(bits[:-1]),bits[-1]
        try:
            mod = import_module(module)
        except ImportError as e:
            raise ImproperlyConfigured('Error importing template source loader {0}: "{1}"'.format(module, e))
        try:
            TemplateLoader = getattr(mod, attr)
        except AttributeError as e:
            raise ImproperlyConfigured('No template loader attribute {0} in {1}: "{2}"'.format(attr, module, e))

        fargs = [arg if not hasattr(arg,'__call__') else arg() for arg in args]
        return TemplateLoader(*fargs)

    def load_template_source(self, template_name, dirs=None):
        for env in self.envs:
            try:
                content, location, _ = env.loader.get_source(env,template_name)
                return content, location
            except TemplateNotFound:
                continue
        raise TemplateNotFound
