from djpcms import views
from djpcms.template import loader
from djpcms.utils import force_str, routejoin
from djpcms.utils.text import nicename
from djpcms.html import ObjectDefinition
from djpcms.core.exceptions import ImproperlyConfigured

__all__ = ['AdminSite',
           'ApplicationGroup',
           'AdminApplication']

ADMIN_GROUP_TEMPLATE = ('admin/groups.html',
                        'djpcms/admin/groups.html')

ADMIN_APPLICATION_TEMPLATE = ('admin/groups.html',
                              'djpcms/admin/groups.html')


class ApplicationGroup(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer a group of :class:`djpcms.views.Applications`.'''
    list_display = ['name','actions']
    home = views.GroupView(in_navigation = 1,
                           view_template = ADMIN_APPLICATION_TEMPLATE)
    

class AdminSite(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer models in groups.'''
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
      
    
class AdminApplication(views.ModelApplication):
    view_template = 'djpcms/admin/viewtemplate.html'
    
    search = views.SearchView()
    add    = views.AddView()
    view   = views.ViewView()
    change = views.ChangeView()
    delete = views.DeleteView()
    
    def render_object(self, djp):
        '''Render an object in its object page.
        This is usually called in the view page of the object.
        '''
        change = self.getview('change')(djp.request, **djp.kwargs)
        ctx = {'view':force_str(ObjectDefinition(self, djp)),
               'change':change.render()}
        return loader.render(self.view_template,ctx)
    