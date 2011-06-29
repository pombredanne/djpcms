from datetime import datetime

import djpcms
from djpcms import views, html, forms, sites
from djpcms.html import icons
from djpcms.template import loader
from djpcms.apps.included.admin import AdminApplication
from djpcms.utils import mark_safe
from djpcms.utils.text import nicename
from djpcms.utils.dates import nicetimedelta

from stdnet.lib import redis
from stdnet.lib.redisinfo import redis_info, RedisData, RedisDbData,\
                                 RedisDataFormatter
from stdnet.orm import model_iterator


__all__ = ['RedisMonitorApplication',
           'StdModelApplication']


class ServerForm(forms.Form):
    host = forms.CharField(initial = 'localhost')
    port = forms.IntegerField(initial = 6379)
    notes = forms.CharField(widget = html.TextArea, required = False)
    
    
class Formatter(RedisDataFormatter):
    
    def format_bool(self, val):
        if not val:
            return icons.circle_close()
        else:
            return icons.circle_check()
                
    def format_name(self, name):
        return nicename(name)
    
    def format_date(self, t):
        try:
            d = datetime.fromtimestamp(t)
            return '%s %s' % (format(d.date(),sites.settings.DATE_FORMAT),
                              time_format(d.time(),sites.settings.TIME_FORMAT)) 
        except:
            return ''
        
    def format_timedelta(self, td):
        return nicetimedelta(td)


class RedisMixin(object):
    
    def get_redis(self, instance, db = None):
        r = redis.Redis(host = instance.host,
                        port = instance.port,
                        db = db)
        r.database_instance = instance
        return r
    
    def get_redisdb(self, instance, db):
        r = self.get_redis(instance, db = int(db))
        return RedisDbData(rpy = r)
        

class RedisKeyApplication(RedisMixin, views.ModelApplication):
    '''Display information about keys in one database.'''
    has_plugins = False
    astable = True
    list_per_page = 250
    description = 'Database {0[db]}'
    headers = ('key','type','length','time to expiry')
    model_id_name = 'db'
    
    home = views.ViewView('', description = 'Redis database key view')
    
    def get_from_parent_object(self, parent, db):
        return self.get_redisdb(parent, db)
    
    def objectbits(self, obj):
        if isinstance(obj,self.model):
            id = obj.rpy.database_instance.id
            return {'id':id,'db':obj.id}
        else:
            return {}
    
    def render_object(self, djp):
        qs = djp.instance.stats()
        p = html.Paginator(djp.request, qs,
                           per_page = self.list_per_page)
        return html.Table(djp,
                          self.headers,
                          p.qs,
                          paginator = p).render()


class RedisDbApplication(RedisMixin,views.ModelApplication):
    has_plugins = False
    astable = True
    list_display = ('db','keys','expires')
    actions = [('bulk_delete','flush',djpcms.DELETE)]
    
    home = views.SearchView()
    keys = RedisKeyApplication('/(?P<db>\d+)/',
                               RedisDbData,parent='home')
    
    def basequery(self, djp):
        instance = djp.parent.instance
        r = self.get_redis(instance)
        try:
            info = redis_info(r)
        except redis.ConnectionError:
            return ()
        return info.databases
    
    def get_instances(self, djp):
        data = djp.request.REQUEST
        if 'ids[]' in data:
            instance = djp.parent.instance
            return [self.get_redisdb(instance,db) for db in data.getlist('ids[]')]    
    

class RedisMonitorApplication(RedisMixin,AdminApplication):
    inherit = True
    form = ServerForm
    list_per_page = 100
    formatter = Formatter()
    
    list_display = ['host','port','notes']
    redisdb = RedisDbApplication('/db/', RedisData, parent = 'view')
    template_view = ('monitor/monitor.html',)
        
    def render_object_view(self, djp):
        r = self.get_redis(djp.instance)
        try:
            info = redis_info(r, formatter = self.formatter)
        except redis.ConnectionError:
            left_panels = [{'name':'Server','value':'No Connection'}]
            right_panels = ()
        else:
            panels = info.panels()
            left_panels = ({'name':k,
                            'value':html.ObjectDefinition(self,djp,v)} for k,v in panels.items())
            view = self.getview('db-home')(djp.request,**djp.kwargs)
            dbs = view.render()
            right_panels = ({'name':'Databases',
                             'value':dbs},)
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
    
