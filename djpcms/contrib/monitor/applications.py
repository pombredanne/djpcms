from djpcms.template import loader
from djpcms.html import LazyRender
from djpcms.contrib.monitor import views
from djpcms.apps.included.admin import AdminApplication
from djpcms.html import Table, ObjectDefinition
from djpcms.utils import mark_safe

from stdnet.lib import redis
from stdnet.orm import model_iterator

from .redisinfo import redis_info, ServerForm


__all__ = ['RedisMonitorApplication',
           'StdModelApplication']
    

class RedisMonitorApplication(AdminApplication):
    inherit = True
    form = ServerForm
    list_per_page = 100
    template_view = ('monitor/redis_monitor.html',)
    
    db = views.RedisDbView(regex = '(?P<db>\d+)', parent = 'view')
    flush = views.RedisDbFlushView(regex = 'flush', parent = 'db')
    
    def get_redis(self, instance, db = None):
        return redis.Redis(host = instance.host,
                           port = instance.port,
                           db = db)
        
    def render_object(self, djp):
        instance = djp.instance
        change = self.getview('change')(djp.request, **djp.kwargs)
        r = self.get_redis(instance)
        try:
            info = redis_info(r.info(),djp.url)
        except redis.ConnectionError:
            panels = [{'name':'Server','value':'No Connection'}]
            databases = ''
        else:
            databases = Table(djp, **info.pop('keys')).render()
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
    '''Display Information about a stdnet model'''
    object_display = ['name','app_label','database','keyprefix','timeout']
    list_display = ['name','app_label','database','keyprefix','timeout']
    search = views.View(astable = True)
    app = views.View(astable = True,
                     regex = '(?P<app>{0})'.format(views.SLUG_REGEX),
                     title = lambda djp : djp.kwargs['app'])
    view = views.View(regex = '(?P<model>{0})'.format(views.SLUG_REGEX),
                      parent = 'app',
                      renderer = lambda djp: djp.view.appmodel.render_model(djp),
                      title = lambda djp: djp.view.appmodel.model_title(djp))
    flush = views.StdModelDeleteAllView(regex = 'flush',
                                        parent = 'view')
    
    def basequery(self, djp):
        models = model_iterator(djp.root.settings.INSTALLED_APPS)
        application = djp.kwargs.get('app',None)
        mname = djp.kwargs.get('model',None)
        done = False
        for model in models:
            if done:
                raise StopIteration
            meta = model._meta
            app = meta.app_label
            name = meta.name
            if application:
                if application != app:
                    continue
                elif mname and mname != name:
                    continue
                else:
                    djp.kwargs['instance'] = meta
                    done = True
            yield meta
            #view = self.getview('view')(djp.request, app = app,
            #                            model = name)
            #appview = self.getview('app')(djp.request, app = app)
            #if view:
            #    name = mark_safe('<a href="{0}" title="{1} model">{1}</a>'.format(view.url,name))
            #if appview:
            #    app = mark_safe('<a href="{0}" title="{1} application group">{1}</a>'.format(appview.url,app))
            #yield (name,app,str(meta.cursor))
            
    def objectbits(self, obj):
        return {'app':obj.app_label,
                'model':obj.name}
        
    def render(self, djp):
        qs = self.basequery(djp)
        return self.render_query(djp, qs)
    
    def get_instance(self, djp):
        model = djp.instance
        if not model:
            list(self.basequery(djp))
            model = djp.instance
        return model
    
    def model_title(self, djp):
        model = self.get_instance(djp)
        if model:
            return model.name
        
    def render_model(self, djp):
        model = self.get_instance(djp)
        if not model:
            raise djp.http.Http404('Model {0[app]}.{0[name]} not available'.format(djp.kwargs))
        info = ObjectDefinition(self, djp)
        return loader.render('monitor/stdmodel.html',
                             {'meta':model,
                              'info':info})
    
