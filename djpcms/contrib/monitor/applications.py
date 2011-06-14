import djpcms
from djpcms import views, html
from djpcms.template import loader
from djpcms.apps.included.admin import AdminApplication
from djpcms.utils import mark_safe

from stdnet.lib import redis
from stdnet.orm import model_iterator

from .redisinfo import redis_info, ServerForm, RedisData


__all__ = ['RedisMonitorApplication',
           'StdModelApplication']


class RedisMixin(object):
    
    def get_redis(self, instance, db = None):
        return redis.Redis(host = instance.host,
                           port = instance.port,
                           db = db)
        

class RedisDbView(views.ModelApplication):
    '''Display information about keys in one database.'''
    astable = True
    #default_title = 'Database {0[db]}'
    headers = ('key','type','length','time to expiry')
    
    home = views.SearchView()
    
    def basequery(self, djp, **kwargs):
        r = self.appmodel.get_redis(djp.instance, db = djp.kwargs['db'])
        return DbQuery(djp,r)
    
    def render(self, djp):
        r = self.appmodel.get_redis(djp.instance, db = djp.kwargs['db'])
        qs = DbQuery(djp,r)
        p = Paginator(djp.request, qs, per_page = self.appmodel.list_per_page)
        return Table(djp,
                     self.headers,
                     p.qs,
                     appmodel = self,
                     paginator = p).render()


class RedisDbApplication(RedisMixin,views.ModelApplication):
    astable = True
    list_display = ('db','keys','expires')
    actions = [('flush','flush',djpcms.DELETE)]
    
    home = views.SearchView()
    view = views.ViewView('/(?P<db>\d+)/')
    
    def basequery(self, djp):
        r = self.get_redis(djp.parent.instance)
        try:
            info = redis_info(r.info(),djp.url)
        except redis.ConnectionError:
            return ()
        return info._panels['keys']
    
    def ajax__flush(self, djp):
        data = djp.request.REQUEST
        r = self.appmodel.get_redis(djp.instance, db = djp.kwargs['db'])
        keys = len(r.keys())
        return jhtmls(identifier = 'td.redisdb%s.keys' % r.db,
                      html = keys)
    
    

class RedisMonitorApplication(RedisMixin,AdminApplication):
    inherit = True
    form = ServerForm
    list_per_page = 100
    redisdb = RedisDbApplication('/db/', RedisData, parent = 'view')
    template_view = ('monitor/monitor.html',)
        
    def render_object_view(self, djp):
        r = self.get_redis(djp.instance)
        try:
            info = redis_info(r.info(),djp.url)
        except redis.ConnectionError:
            left_panels = [{'name':'Server','value':'No Connection'}]
            right_panels = ()
        else:
            left_panels = ({'name':k,
                            'value':html.ObjectDefinition(self,djp,v)} for k,v in info.items())
            dbs = html.Table(djp, appmodel = self, **info.pop('keys'))
            right_panels = ({'name':'Databases',
                             'value':dbs.render()},)
        return loader.render(self.template_view,
                            {'left_panels':left_panels,
                             'right_panels':right_panels})
    
    def dburl(self, db):
        dbview = self.getview('db')
        djp = view(request, db = db)
        return djp.url
    
    

class StdModelDeleteAllView(views.ModelView):
    _methods = ('post',)
    
    def default_post(self, djp):
        self.model.flush()
        next,curr = forms.next_and_current(djp.request)
        return jredirect(next or curr)
    
    
    
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
    flush = StdModelDeleteAllView(regex = 'flush', parent = 'view')
    
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
        info = html.ObjectDefinition(self, djp)
        return loader.render('monitor/stdmodel.html',
                             {'meta':model,
                              'info':info})
    
