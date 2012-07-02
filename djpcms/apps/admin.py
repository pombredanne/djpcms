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
from djpcms import views, html
from djpcms.html import Widget, WidgetMaker
from djpcms.utils.httpurl import iteritems, remove_end_slashes
from djpcms.utils.importer import import_module
from djpcms.utils.text import nicename
from djpcms.cms import ImproperlyConfigured

__all__ = ['AdminSite',
           'ApplicationGroup',
           'AdminApplicationSimple',
           'AdminApplication',
           'TabView',
           'make_admin_urls']


class ApplicationGroup(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer a group of :class:`djpcms.views.Applications`.'''
    has_plugins = False
    pagination = html.Pagination(('name','actions'),
                                 ajax = False,
                                 footer = False,
                                 html_data = {'options':{'sDom':'t'}})
    
    home = views.View(in_nav=1)
    
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
    pagination = html.Pagination(layout=html.accordion,
                                 ajax=False,
                                 size=None)
    
    home = views.View(in_nav=1, icon='admin')
    
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
            yield a, g['body']
      

class AdminApplicationSimple(views.Application):
    pagination = html.Pagination(('__str__',))
    has_plugins = False
    search = views.SearchView()
    delete_all = views.DeleteAllView()
    view = views.ViewView()
    delete = views.DeleteView()
    
    
class TabView(views.ObjectView):
    
    def get_views(self, request):
        appmodel = request.view.appmodel
        for r in views.application_views(request, exclude=('delete',)):
            order = appmodel.views_ordering.get(r.view.name,100)
            yield order,r
            
    def render(self, request):
        instance = request.instance
        tabs = html.tabs().addData('ajax', True)
        first = True
        for order, elem in sorted(self.get_views(request), key=lambda v: v[0]):
            # we render so that we add javascript if it is needed
            text = elem.view.render()
            link = views.application_link(elem, asbutton=False)
            tabs.addtab(link, text)
        return tabs
     
     
class AdminApplication(views.Application):
    has_plugins = False
    views_ordering = {'view':0,'change':1}
    pagination = html.Pagination(('__str__',))
    home = views.SearchView()
    delete_all = views.DeleteAllView()
    add = views.AddView()
    tabview = TabView('/<id>/')
    view = views.ViewView('/view', parent_view='tabview')
    change = views.ChangeView(parent_view='tabview')
    delete = views.DeleteView(parent_view='tabview')
    
    def view_for_instance(self, request, instance):
        return self.views.get('tabview')


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
            route  = getattr(admin,'ROUTE',mname)
            yield (name, route, urls)
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
    def __init__(self, grouping=None, name='admin', **params):
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
                rname = remove_end_slashes(route)
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