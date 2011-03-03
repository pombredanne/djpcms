'''Twisted asyncronous handler for djpcms
'''
from djpcms.apps.included.static import application_map

from .resources import builserver


class Server(object):
    
    def __init__(self, handler, port = 0, pool = None,
                 withpool = False, reactor_type = None,
                 **kwargs):
        self.pool = pool
        self.reactor_type = reactor_type
        if pool is None and withpool:
            self.pool = getpool(0)
            pool = self.pool
    
    def build(self):
        reactor = get_reactor(self.reactor_type)
        if not hasattr(self,'root'):
            from .resources import builserver
            builserver(self, reactor)
        return self
    
    def serve(self):
        self.build()
        get_reactor(self.reactor_type).run()
    
    def _stop(self):
        #Stop the server in an orderly way
        if self.pool:
            self.pool.wait()
            

def django_media(root,settings,path):
    from unuk.contrib.txweb.resources import static, Favicon
    media = settings.MEDIA_URL
    mroot = settings.MEDIA_ROOT
    site  = 'site'
    #os.path.split(path)[1]
    settings.ADMIN_MEDIA_PREFIX = '{0}admin/'.format(media)
    if not mroot:
        mroot = os.path.join(path,media[1:-1])
    amed = application_map(settings.INSTALLED_APPS)
    media = static.File(mroot)
    root.putChild('media', media)
    favicon = os.path.join(mroot,site,'favicon.ico')
    root.putChild('favicon.ico', Favicon(favicon))
    for item in amed.values():
        if item.exists:
            addmedia(media, item.name, item.fullpath)
    

def addmedia(media, url, path):
    from twisted.web import static
    app = static.File(path)
    media.putChild(url, app)

