from djpcms import views, UnicodeMixin
from djpcms.template import loader
from djpcms.core.orms import table
from djpcms.utils import force_str, routejoin
from djpcms.utils.text import nicename
from djpcms.html import ObjectDefinition
from djpcms.core.exceptions import ImproperlyConfigured

__all__ = ['AdminSite',
           'ApplicationGroup',
           'AdminApplication']
        

class ApplicationGroup(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer a group of :class:`djpcms.views.Applications`.'''
    list_display = ['name','actions']
    template_name = ('admin/applications.html',
                     'djpcms/admin/applications.html')
    home = views.View(in_navigation = 1)
    
    def render(self, djp):
        url = djp.url
        ctx = {}
        return loader.render(self.template_name,ctx)

class AdminSite(views.Application):
    '''An :class:`djpcms.views.Application` class for
administer models in groups.'''
    template_name = ('admin/groups.html',
                     'djpcms/admin/groups.html')
    home = views.View(in_navigation = 1)
    
    def render(self, djp):
        url = djp.url
        ctx = {'items':djp.children()}
        return loader.render(self.template_name,ctx)
    
    
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
    