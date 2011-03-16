from djpcms.template import loader
from djpcms.html import LazyRender
from djpcms.contrib.monitor import views
from djpcms.apps.included.admin import AdminApplication
from djpcms.html import table, ObjectDefinition

from stdnet.lib import redis

from .redisinfo import redis_info, RedisServerForm


class RedisMonitorApplication(AdminApplication):
    inherit = True
    form = RedisServerForm
    list_per_page = 100
    template_view = ('monitor/redis_monitor.html',)
    
    db = views.RedisDbView(regex = '(?P<db>\d+)', parent = 'view')
    flush = views.RedisDbFlushView(regex = 'flush', parent = 'db')
    
    def get_redis(self, instance, db = None):
        return redis.Redis(host = instance.host,
                           port = instance.port,
                           db = db)
        
    def render_object(self, djp):
        '''Render an object in its object page.
        This is usually called in the view page of the object.
        '''
        instance = djp.instance
        change = self.getview('change')(djp.request, **djp.kwargs)
        r = self.get_redis(instance)
        try:
            info = redis_info(r.info(),djp.url)
        except redis.ConnectionError:
            panels = [{'name':'Server','value':'No Connection'}]
            databases = ''
        else:
            databases = table(djp, **info.pop('keys'))
            panels = ({'name':k,'value':ObjectDefinition(self,djp,v)} for k,v in info.items())
        view = loader.render(self.template_view,
                            {'panels':panels,
                             'databases':databases})
        ctx = {'view':view,
               'change':change.render()}
        return loader.render(self.view_template,ctx)
    
    def dburl(self, db):
        dbview = self.getview('db')
        djp = view(request, db = db)
        return djp.url
    
    
class StdModelApplication(views.ModelApplication):
    search      = views.SearchView()
    information = views.StdModelInformationView(regex = 'info')
    flush       = views.StdModelDeleteAllView(regex = 'flush')