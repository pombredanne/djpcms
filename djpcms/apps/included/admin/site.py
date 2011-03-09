'''An application which displays a table with all applications
registered in the same ApplicationSite::

    from djpcms.apps.included.admin import SiteAdmin
    from djpcms.apps.included.sitemap import SiteMapView
    
    admin_urls = (
                  SiteAdmin('/', name = 'admin'),
                  SiteMapView('/sitemap/', name = 'sitemap'),
                  .
                  .
                  .
                 )
                  
'''
from djpcms import views, UnicodeMixin
from djpcms.template import loader
from djpcms.core.orms import table
from djpcms.utils import force_str
from djpcms.utils.text import nicename
from djpcms.html import ObjectDefinition

__all__ = ['SiteAdmin',
           'ApplicationList',
           'AdminApplication']


def jqueryicon(url,icon_class):
    if not url:
        return ''
    return '<a class="icon {0}"></a>'.format(icon_class)


class AppList(UnicodeMixin):
    
    def __init__(self, app, djp):
        self.app = app
        self.djp = djp
        
    def __iter__(self):
        djp = self.djp
        request = djp.request
        site = djp.site
        appmodel = self.app.appmodel
        for app in site._nameregistry.values():
            if app is appmodel:
                continue
            view = app.root_view
            vdjp = view(djp.request)
            url = vdjp.url
            if url:
                name = nicename(app.name)
                addurl = jqueryicon(app.addurl(request),'ui-icon-circle-plus')
                yield ('<a href="{0}">{1}</a>'.format(url,name),addurl)


class ApplicationList(views.View):
    
    def render(self, djp):
        site = djp.site
        appmodel = self.appmodel
        headers = self.headers or appmodel.list_display
        if hasattr(headers,'__call__'):
            headers = headers(djp)
        ctx = table(headers, AppList(self,djp), djp, appmodel)
        return loader.render('djpcms/tablesorter.html',ctx)
        

class SiteAdmin(views.Application):
    list_display = ['name','actions']
    home = ApplicationList(title = lambda djp : 'Admin', in_navigation = 1)
    
    
    
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
    