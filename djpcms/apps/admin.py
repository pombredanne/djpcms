'''\
Dependencies: **None**

An application which displays a table with all applications
registered in the same ApplicationSite::

    from djpcms.apps.admin import AdminSite
    from djpcms.apps.sitemap import SiteMapView
    
    admin_urls = (
                  SiteAdmin('/', name = 'admin'),
                  SiteMapView('/sitemap/', name = 'sitemap'),
                 )
                  
'''
from py2py3 import iteritems

from djpcms import views, html
from djpcms.html import Widget, ContextRenderer
from djpcms.utils import force_str, routejoin
from djpcms.utils.urls import closedurl
from djpcms.utils.importer import import_module
from djpcms.utils.text import nicename
from djpcms.core.exceptions import ImproperlyConfigured

__all__ = ['AdminSite',
           'ApplicationGroup',
           'AdminApplicationSimple',
           'AdminApplication',
           'TabView',
           'TabViewMixin',
           'make_admin_urls']


ADMIN_GROUP_TEMPLATE = ('admin/groups.html',
                        'djpcms/admin/groups.html')

ADMIN_APPLICATION_TEMPLATE = ('admin/groups.html',
                              'djpcms/admin/groups.html')
            

class TabView(views.ObjectItem):
    '''A function for rendering a model instance
like in the admin interface. Using jQuery UI tabs.
This is usually called in the view page of the object.
    
:parameter djp: instance of a :class:`djpcms.views.DjpResponse`'''
    
    view_template = 'djpcms/admin/viewtemplate.html'
        
    def inner(self, djp, widget, keys):
        ctx = []
        appmodel = widget.internal['appmodel']
        instance = widget.internal['instance']
        request = djp.request
        for view in appmodel.object_views:
            if 'get' not in view.methods(request):
                continue
            if isinstance(view,views.ViewView):
                html = self.render_object_view(djp, appmodel, instance)
            else:
                dv = view(djp.request, **djp.kwargs)
                try:
                    dv.url
                except:
                    continue
                html = dv.render()
            name = view.name
            o  = appmodel.views_ordering.get(name,100)
            ctx.append({'name':view.description or nicename(name),
                        'id':name,
                        'value':html,
                        'order': o})
        ctx = {'views':sorted(ctx, key = lambda x : x['order'])}
        return ContextRenderer(djp,ctx,template=self.view_template)
    
    def  render_object_view(self, djp, appmodel, instance):
        if 'object' in appmodel.object_widgets:
            return appmodel.render_object(djp,instance,context='object')
        else:
            return ''


class TabViewMixin(object):
    views_ordering = {'view':0,'change':1}
    object_widgets = views.extend_widgets({'home':TabView(),
                                           'object':views.ObjectDef()})
    pagination = html.Pagination(('__str__',))


class ApplicationGroup(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer a group of :class:`djpcms.views.Applications`.'''
    has_plugins = False
    pagination = html.Pagination(('name','actions'),
                                 ajax = False,
                                 footer = False,
                                 html_data = {'options':{'sDom':'t'}})
    
    home = views.GroupView(in_nav = 1)
    
    def table_generator(self, djp, headers, qs):
        request = djp.request
        for r in qs:
            title = r.title
            appmodel = r.view.appmodel
            home = appmodel.root_view(request,**djp.kwargs)
            links = ''.join((l[1] for l in views.application_links(\
                                views.application_views(djp))))
            yield ('<a href="{0}">{1}</a>'.format(home.url,title),links)
    

class AdminSite(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer models in groups.'''
    has_plugins = False
    in_nav = 100
    query_template = ADMIN_GROUP_TEMPLATE
    pagination = html.Pagination(widget_factory = html.accordion,
                                 ajax = False,
                                 size = None)
    
    home = views.GroupView(in_nav = 1)
    
    def groups(self, djp):
        for child in djp.auth_children():
            yield {'body':child.render(),
                   'title':child.title,
                   'url': child.url}
            
    def basequery(self, djp):
        for g in sorted(self.groups(djp), key = lambda x : x['title']):
            url = g['url']
            if url:
                a = Widget('a', g['title'], href = url)
            else:
                a = g['title']
            yield a,g['body']
      

class AdminApplicationSimple(TabViewMixin,views.Application):
    has_plugins = False
    search = views.SearchView()
    delete_all = views.DeleteAllView()
    view   = views.ViewView()
    delete = views.DeleteView()
    
    
class AdminApplication(AdminApplicationSimple):
    inherit = True
    add    = views.AddView()
    change = views.ChangeView()


def get_admins(INSTALLED_APPS):
    for apps in INSTALLED_APPS:
        if apps.startswith('django.'):
            continue
        try:
            mname = apps.split('.')[-1]
            admin = import_module('{0}.admin'.format(apps))
            urls  = getattr(admin,'admin_urls',None)
            if not urls:
                continue
            name = getattr(admin,'NAME',mname)
            route  = closedurl(getattr(admin,'ROUTE',mname))
            yield (name,route,urls)
        except ImportError:
            continue
        
        
def make_admin_urls(INSTALLED_APPS, grouping = None, name = 'admin', **params):
    '''Return a one element tuple containing an
:class:`djpcms.apps.included.admin.AdminSite`
application for displaying the admin site. All application with an ``admin``
module specifying the admin application will be included.

:parameter params: key-value pairs of extra parameters for input in the
               :class:`djpcms.apps.included.admin.AdminSite` constructor.'''
    adming = {}
    agroups = {}
    if grouping:
        for url,v in grouping.items():
            for app in v['apps']:
                if app not in adming:
                    adming[app] = url
                    if url not in agroups:
                        v = v.copy()
                        v['urls'] = ()
                        agroups[url] = v
    groups = []
    for name_,route,urls in get_admins(INSTALLED_APPS):
        if urls:
            rname = route[1:-1]
            if rname in adming:
                url = adming[rname]
                agroups[url]['urls'] += urls
            else:
                adming[rname] = route
                agroups[route] = {'name':name_,
                                  'urls':urls}
                
    for route,data in agroups.items():
        groups.append(ApplicationGroup(route,
                                       name = data['name'],
                                       routes = data['urls']))
        
    # Create the admin application
    admin = AdminSite('/', name = name, routes = groups, **params)
    return (admin,)