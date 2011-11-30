from djpcms.utils import js, media

from .wrappers import Request


class djpcmsinfo(object):
    '''Holds information and data to be reused during a single request.
This is used as a way to speed up responses as well as for
managing settings.'''
    def __init__(self, view, urlargs):
        self.view = view
        self.urlargs = urlargs if urlargs is not None else {}
        self.page = None
        self.instance = None
        self.context_cache = None
        self.environ = {}
        self._djp_instance_cache = {}
    
    def __getitem__(self, key):
        return self.environ[key]
    
    def __setitem__(self, key, value):
        self.environ[key] = value
        
    def get(self, key, default = None):
        return self.environ.get(key,default)
        
    @property
    def media(self):
        if not hasattr(self,'_media'):
            settings = self.view.settings
            m = media.Media(settings = settings)
            m.add_js(js.jquery_paths(settings))
            m.add_js(settings.DEFAULT_JAVASCRIPT)
            m.add_css(settings.DEFAULT_STYLE_SHEET)
            m.add(self.view.media(self))
            self._media = m
        return self._media
    
    def request(self, environ):
        if self.view:
            if isinstance(request,dict):
                request = Request(request)
            return self.view(request, **self.kwargs)
    
    def djp_from_instance(self, view, instance):
        if instance and instance.id: 
            return self._djp_instance_cache.get((view,instance))
    
    def add_djp_instance_cache(self, djp, instance):
        if instance and getattr(instance,'id',None):
            self._djp_instance_cache[(djp.view,instance)] = djp
    
    @property
    def root(self):
        return self.site.root
    
    @property
    def tree(self):
        return self.site.tree
    
    