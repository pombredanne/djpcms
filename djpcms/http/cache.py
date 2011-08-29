from djpcms.utils import js


class djpcmsinfo(object):
    '''Holds information and data to be reused during a single request.
This is used as a way to speed up responses as well as for
managing settings.'''
    def __init__(self,view,kwargs,page=None,site=None,instance=None):
        self.view = view
        self.kwargs = kwargs if kwargs is not None else {}
        self.page = page
        self.instance = instance
        self.context_cache = None
        self.site = site = view.site if view else site
        
    def context(self, request = None):
        if not hasattr(self,'_context_cache'):
            if request:
                self._context_cache = context_cache = {}
                processors = self.site.template_context()
                if processors is not None:
                    for processor in processors:
                        context_cache.update(processor(request))
            else:
                return {}
        return self._context_cache
            
    @property
    def media(self):
        if not hasattr(self,'_media'):
            settings = self.site.settings
            vmedia = self.view.media()
            media = vmedia.__class__(settings = settings)
            media.add_js(js.jquery_paths(settings))
            media.add_js(settings.DEFAULT_JAVASCRIPT)
            media.add(vmedia)
            self._media = media
        return self._media
    
    def djp(self, request = None):
        if self.view:
            return self.view(request, **self.kwargs)
    
    @property
    def root(self):
        return self.site.root
    
    @property
    def tree(self):
        return self.site.tree
    
    