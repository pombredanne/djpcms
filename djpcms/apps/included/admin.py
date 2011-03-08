from djpcms import views, UnicodeMixin
from djpcms.template import loader
from djpcms.core.orms import table
from djpcms.utils.text import nicename


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
    home = ApplicationList(title = lambda djp : 'Admin',
                           in_navigation = 1)
    