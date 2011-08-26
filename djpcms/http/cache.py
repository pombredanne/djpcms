JQUERY_PATH = 'https://ajax.googleapis.com/ajax/libs/jquery/{0}/jquery.min.js'
JQUERY_UI_PATH = 'https://ajax.googleapis.com/ajax/libs/jqueryui/\
{0}/jquery-ui.min.js'

def jquery_path(settings):
    v = settings.JQUERY_VERSION
    if v:
        return JQUERY_PATH.format(v)

def jquery_ui_path(settings):
    v = settings.JQUERY_UI_VERSION
    if v:
        return JQUERY_UI_PATH.format(v)
    
def jquery_paths(settings):
    jq = jquery_path(settings)
    if jq:
        return jq,jquery_ui_path(settings)
    return jq,None



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
        
    @property
    def media(self):
        if not hasattr(self,'_media'):
            settings = self.site.settings
            vmedia = self.view.media()
            media = vmedia.__class__(settings = settings)
            media.add_js(jquery_paths(settings))
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
    
    