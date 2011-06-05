from py2py3 import iteritems

from djpcms import views
from djpcms.template import loader
from djpcms.utils import force_str, routejoin
from djpcms.utils.text import nicename
from djpcms.html import ObjectDefinition, icons
from djpcms.core.exceptions import ImproperlyConfigured

__all__ = ['AdminSite',
           'ApplicationGroup',
           'AdminApplicationSimple',
           'AdminApplication']

ADMIN_GROUP_TEMPLATE = ('admin/groups.html',
                        'djpcms/admin/groups.html')

ADMIN_APPLICATION_TEMPLATE = ('admin/groups.html',
                              'djpcms/admin/groups.html')


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
            url = appmodel.root_view(request,**djp.kwargs).url
            addurl = appmodel.addurl(request)
            if addurl:
                a = icons.circle_plus(addurl,'','add {0}'.format(title))
            else:
                a = ''
            yield ('<a href="{0}">{1}</a>'.format(url,title),a)
    

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
      

class AdminApplicationSimple(views.ModelApplication):
    view_template = 'djpcms/admin/viewtemplate.html'
    ordering = {'view':0,'change':1}
    has_plugins = False
    search = views.SearchView()
    view   = views.ViewView()
    delete = views.DeleteView()
    
    def render_object(self, djp):
        '''Render an object in its object page.
        This is usually called in the view page of the object.
        '''
        ctx = []
        for name,view in iteritems(self.views):
            if view.object_view:
                if not isinstance(view,views.DeleteView):
                    if name == 'view':
                        html = self.render_object_view(djp)
                    else:
                        dv = view(djp.request, **djp.kwargs)
                        try:
                            dv.url
                        except:
                            continue
                        html = dv.render()
                    o  = self.ordering.get(name,100)
                    ctx.append({'name':nicename(name),
                                'id':name,
                                'value':html,
                                'order': o})
        ctx = {'views':sorted(ctx, key = lambda x : x['order'])}
        return loader.render(self.view_template,ctx)
    
    def render_object_view(self, djp):
        return force_str(ObjectDefinition(self, djp))
    
    
class AdminApplication(AdminApplicationSimple):
    inherit = False
    has_plugins = False
    search = views.SearchView()
    add    = views.AddView()
    view   = views.ViewView()
    change = views.ChangeView()
    delete = views.DeleteView()

