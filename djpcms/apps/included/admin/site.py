from py2py3 import iteritems

from djpcms import views, html
from djpcms.template import loader
from djpcms.utils import force_str, routejoin
from djpcms.utils.text import nicename
from djpcms.html import ObjectDefinition, application_links
from djpcms.core.exceptions import ImproperlyConfigured

__all__ = ['AdminSite',
           'ApplicationGroup',
           'AdminApplicationSimple',
           'AdminApplication',
           'TabView',
           'TabViewMixin']


ADMIN_GROUP_TEMPLATE = ('admin/groups.html',
                        'djpcms/admin/groups.html')

ADMIN_APPLICATION_TEMPLATE = ('admin/groups.html',
                              'djpcms/admin/groups.html')


class TabView(html.ObjectItem):
    '''A function for rendering a model instance
    like in the admin interface. Using jQuery UI tabs.
    This is usually called in the view page of the object.
    
    :parameter self: instance of a :class:`djpcms.views.ModelApplication`
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
                html = self.render_object_view(djp,appmodel,instance)
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
        return loader.render(self.view_template,ctx)

    def render_object_view(self, djp, appmodel, instance):
        return force_str(ObjectDefinition(appmodel, djp, instance = instance))


class TabViewMixin(object):
    views_ordering = {'view':0,'change':1}
    object_widgets = views.extend_widgets({'home':TabView()})


class ApplicationGroup(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer a group of :class:`djpcms.views.Applications`.'''
    has_plugins = False
    list_display = ('name','actions')
    home = views.GroupView(in_navigation = 1,
                           view_template = ADMIN_APPLICATION_TEMPLATE)
    
    def table_generator(self, djp, headers, qs):
        request = djp.request
        for r in qs:
            title = r.title
            appmodel = r.view.appmodel
            home = appmodel.root_view(request,**djp.kwargs)
            links = ''.join((l[1] for l in application_links(appmodel,
                                                    djp,as_widget=True)))
            yield ('<a href="{0}">{1}</a>'.format(home.url,title),links)
    

class AdminSite(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer models in groups.'''
    has_plugins = False
    in_navigation = 100
    query_template = ADMIN_GROUP_TEMPLATE
    home = views.GroupView(in_navigation = 1)
    
    def groups(self, djp):
        for child in djp.auth_children():
            yield {'body':child.html(),
                   'title':child.title,
                   'url': child.url}
            
    def basequery(self, djp):
        return sorted(self.groups(djp), key = lambda x : x['title'])
    
    def render_query(self, djp, qs):
        return loader.render(self.query_template, {'items':qs})
      

class AdminApplicationSimple(TabViewMixin,views.ModelApplication):
    has_plugins = False
    search = views.SearchView()
    delete_all = views.DeleteAllView()
    view   = views.ViewView()
    delete = views.DeleteView()
    
    
class AdminApplication(AdminApplicationSimple):
    inherit = True
    add    = views.AddView()
    change = views.ChangeView()

