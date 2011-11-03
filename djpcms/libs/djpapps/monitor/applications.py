from datetime import datetime
from copy import deepcopy

import djpcms
from djpcms import views, html, forms, ajax, ALL_REGEX, SLUG_REGEX
from djpcms.forms.layout import uniforms as uni
from djpcms.html import icons
from djpcms.apps.admin import AdminApplication, TabView
from djpcms.utils import mark_safe
from djpcms.utils.text import nicename
from djpcms.utils.dates import nicetimedelta, smart_time

from stdnet.lib import redis, redisinfo
from stdnet.orm import model_iterator


__all__ = ['RedisMonitorApplication',
           'StdModelApplication']


RedisDbModel = redisinfo.RedisDbData
RedisKeyModel = redisinfo.RedisKeyData


class ServerForm(forms.Form):
    host = forms.CharField(initial = 'localhost')
    port = forms.IntegerField(initial = 6379)
    notes = forms.CharField(widget = html.TextArea, required = False)
    
    
class Formatter(redisinfo.RedisDataFormatter):
    
    def __init__(self):
        self.format_date = smart_time
        self.format_timedelta = nicetimedelta
        self.format_name = nicename
    
    def format_bool(self, val):
        if not val:
            return icons.circle_close()
        else:
            return icons.circle_check()        


class RedisMixin(object):
    
    def get_redis(self, instance, db = None):
        r = redis.Redis(host = instance.host,
                        port = instance.port,
                        db = db)
        r.database_instance = instance
        return r
    
    def get_redisdb(self, server, db):
        if not hasattr(db,'db'):
            r = self.get_redis(server, db = int(db))
            instance = RedisDbModel(rpy = r)
        else:
            instance = db
        instance.server = server
        return instance
        

class InspectKeyForm(forms.Form,RedisMixin):
    INFO_CLASS = 'redis-key-data'
    db = forms.IntegerField(default = 0)
    key = forms.CharField()
    inner_template = '''\
<dl><dt>Type</dt><dd>{0}</dd></dl>\
<dl><dt>Length</dt><dd>{1}</dd></dl>\
<dl><dt>Expire</dt><dd>{2}</dd></dl>
'''
    
    def save(self, commit = True):
        db = self.cleaned_data['db']
        key = self.cleaned_data['key']
        r = self.get_redis(self.instance, db = db)
        v = redisinfo.RedisStats(r)
        typ,l,ttl,enc = v.type_length(key)
        if not typ:
            inner = '<p>key not in database</p>'
        else:
            inner = self.inner_template.format(typ,l,ttl)
        return ajax.jhtmls(inner,
                           '.{0}'.format(self.INFO_CLASS)) 
        
        
InspectKeyFormHtml = forms.HtmlForm(
        InspectKeyForm,
        layout = uni.Layout(
                    uni.Columns('db','key','submits'),
                    html.WidgetMaker(tag = 'div',
                        default_class = 'object-definition {0}'\
                                    .format(InspectKeyForm.INFO_CLASS))),
        inputs = (('check','check'),)
)
        
class RedisTabView(TabView):
    
    def render_object_view(self, djp, appmodel, instance):
        info = instance.redis_info
        if not info:
            left_panels = [{'name':'Server','value':'No Connection'}]
            right_panels = ()
        else:
            panels = info.panels()
            hd = html.DefinitionList
            left_panels = ({\
            'name':k,
            'value':hd(data_stream = ((l['name'],l['value']) for l in panel),
                       cn = 'object-definition')\
                .render(djp)} for k,panel in panels.items())
            view = appmodel.getview('db-home')(djp.request,**djp.kwargs)
            dbs = view.render()
            right_panels = ({'name':'Databases',
                             'value':dbs},)
        return djp.render_template(appmodel.template_view,
                                   {'left_panels':left_panels,
                                    'right_panels':right_panels})
        

class RedisKeyApplication(RedisMixin, views.ModelApplication):
    '''Display information about a key in one database.'''
    has_plugins = False
    list_display = ('key','type','length','time_to_expiry')
    actions = [('bulk_delete','flush',djpcms.DELETE)]
    table_parameters = {'data': {'options':
            {'sDom':'<"H"<"row-selector"><"clear">ilp<"clear">f>t'}}}
    
    search = views.SearchView(astable = True)
    view = views.ViewView(regex = '(?P<key>{0})'.format(ALL_REGEX))
    delete = views.DeleteView()
    expire = views.ChangeView(regex = 'expire')
    
    def basequery(self, djp):
        db = djp.parent.instance
        for k in db.stats().all():
            k.db = db
            yield k
    
    def get_from_parent_object(self, parent, key):
        return parent.get_key(key)


class RedisDbApplication(RedisMixin,views.ModelApplication):
    '''Display information about a single database in the Redis server.'''
    has_plugins = False
    astable = True
    list_display = ('db','keys','expires')
    actions = [('bulk_delete','flush',djpcms.DELETE)]
    table_parameters = {'footer': False,
                        'data': {'options':{'sDom':'<"H"<"row-selector">>t'}}}
    
    home = views.SearchView(astable = True)
    view = views.ViewView(regex = '(?P<db>\d+)')
    keys = RedisKeyApplication('/keys/',
                               RedisKeyModel,
                               parent='view',
                               related_field = 'db')
    
    def basequery(self, djp):
        instance = djp.parent.instance
        if not instance.redis_info:
            raise StopIteration
        for db in instance.redis_info.databases:
            yield self.get_redisdb(instance,db)
    
    def get_from_parent_object(self, parent, db):
        return self.get_redisdb(parent, db)
    
    def get_instances(self, djp):
        data = djp.request.REQUEST
        if 'ids[]' in data:
            instance = djp.parent.instance
            return [self.get_redisdb(instance,db) for db\
                    in data.getlist('ids[]')]
    
    def render_object(self, djp, **kwargs):
        instance = djp.instance
        stats = instance.stats()
        data = stats.data
        view = self.apps['keys'].root_view
        html = view(djp.request, **djp.kwargs).render()
        return html
    

class RedisMonitorApplication(RedisMixin,AdminApplication):
    '''Main application for displaying Redis server information.'''
    inherit = True
    form = ServerForm
    template_view = ('monitor/monitor.html',)
    list_display = ['host','port','notes']
    formatter = Formatter()
    object_widgets = views.extend_widgets({'home':RedisTabView()},
                                          AdminApplication.object_widgets)
    
    redisdb = RedisDbApplication('/db/',
                                 RedisDbModel,
                                 parent = 'view',
                                 related_field = 'server')
    inspect = views.ChangeView(regex = 'inspect',
                               form = InspectKeyFormHtml)
    
    def get_object(self, request, **kwargs):
        instance = super(RedisMonitorApplication,self)\
                        .get_object(request, **kwargs)
        r = self.get_redis(instance)
        try:
            info = redisinfo.redis_info(r, formatter = self.formatter)
        except redis.ConnectionError:
            info = None
        instance.redis_info = info
        return instance
        

class StdModelDeleteAllView(views.ModelView):
    _methods = ('post',)
    
    def default_post(self, djp):
        self.model.flush()
        next,curr = forms.next_and_current(djp.request)
        return jredirect(next or curr)
    
    
    
class StdModelApplication(views.ModelApplication):
    '''Display Information about stdnet models'''
    object_display = ['name','app_label','database','keyprefix','timeout']
    list_display = ['name','app_label','database','keyprefix','timeout']
    table_parameters = {'ajax':False}
    search = views.View(astable = True)
    app = views.View(astable = True,
                     regex = '(?P<app>{0})'.format(SLUG_REGEX),
                     title = lambda djp : djp.kwargs['app'])
    view = views.View(
                  regex = '(?P<model>{0})'.format(SLUG_REGEX),
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
            raise djp.http.Http404('Model {0[app]}.{0[name]} not available'\
                                   .format(djp.kwargs))
        info = html.ObjectDefinition(self, djp)
        return djp.render_template('monitor/stdmodel.html',
                                   {'meta':model,
                                    'info':info})
    
