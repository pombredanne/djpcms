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
            

class TabView(views.ObjectItem):
    '''A function for rendering a model instance
like in the admin interface. Using jQuery UI tabs.
This is usually called in the view page of the object.
    
:parameter djp: instance of a :class:`djpcms.views.DjpResponse`'''
    def view_generator(self, request, widget):
        appmodel = widget.internal['appmodel']
        instance = widget.internal['instance']
        for view in appmodel.object_views:
            req = request.for_path(view.path)
            if 'get' not in req.methods():
                continue
            if isinstance(view,views.ViewView):
                html = req.render(context='object')
            else:
                html = req.render()
            o  = appmodel.views_ordering.get(view.name,100)
            yield o,(view.description,html)
            
    def inner(self, request, widget, keys):
        views = (x[1] for x in sorted(self.view_generator(request,widget),
                                      key = lambda x : x[0]))
        return html.tabs(views).render(request)


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
    
    home = views.View(in_nav = 1)
    
    def table_generator(self, request, headers, qs):
        for child in qs:
            title = child.title
            links = ''.join((l.render() for l in
                              views.application_views_links(child)))
            yield ('<a href="{0}">{1}</a>'.format(child.url,title),links)
    

class AdminSite(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer models in groups.'''
    has_plugins = False
    in_nav = 1000
    pagination = html.Pagination(widget_factory = html.accordion,
                                 ajax = False,
                                 size = None)
    
    home = views.View(in_nav = 1)
    
    def groups(self, request):
        for child in request.auth_children():
            yield {'body':child.render(),
                   'title':child.title,
                   'url': child.url}
            
    def query(self, request, **kwargs):
        for g in sorted(self.groups(request), key = lambda x : x['title']):
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
        
      
class make_admin_urls(object):
    '''Utility class which provide a callable instance for building
admin urls. A callable instance returns a one element tuple containing an
:class:`AdminSite` application for displaying the admin site.
All application with an ``admin`` module specifying the admin
application will be included.

:parameter INSTALLED_APPS: Iterable over application to install.
:parameter grouping: Dictionary for grouping together admin for different
    applications.
:parameter name: name of application.
:parameter params: key-value pairs of extra parameters for input in the
    :class:`AdminSite` constructor.
'''
    def __init__(self, grouping = None, name = 'admin', **params):
        self.grouping = grouping
        self.name = name
        self.params = params
        
    def __call__(self, site):
        settings = site.settings
        adming = {}
        agroups = {}
        if self.grouping:
            for url,v in self.grouping.items():
                for app in v['apps']:
                    if app not in adming:
                        adming[app] = url
                        if url not in agroups:
                            v = v.copy()
                            v['urls'] = ()
                            agroups[url] = v
                            
        for name_,route,urls in get_admins(settings.INSTALLED_APPS):
            if urls:
                rname = route[1:-1]
                if rname in adming:
                    url = adming[rname]
                    agroups[url]['urls'] += urls
                else:
                    adming[rname] = route
                    agroups[route] = {'name':name_,
                                      'urls':urls}
        
        groups = [AdminSite('/', name = self.name, **self.params)]
        for route,data in agroups.items():
            groups.append(ApplicationGroup(route,
                                           name = data['name'],
                                           routes = data['urls']))
            
        return tuple(groups)