from djpcms.template import loader
from djpcms.forms import HtmlForm, HtmlWidget
from djpcms.views import appsite, appview

from .forms import ShortPageForm



class EditingPanel(HtmlWidget):
    template = 'djpcms/content/edit_panel.html'
    tag = 'div'
    
    def inner(self, djp):
        view = djp.view
        context = {'form': view.get_form(djp).render(djp)}
        return loader.render(self.template,context)
        


class editPageView(appview.ChangeView):
    editing_panel = EditingPanel
    
    def get_context(self, djp):
        vdjp    = self.appmodel.underlying(djp)
        context = vdjp.view.get_context(vdjp,editing=True)
        context['page_url'] = vdjp.url
        context['editing_panel'] = self.editing_panel(cn = 'djpcms-editing').render(djp)
        context['bodybits'] = loader.mark_safe(' class="edit"')
        return context
    

PageForm = HtmlForm(ShortPageForm)    


class PageApplication(appsite.ModelApplication):
    '''Application for inline editing of pages'''    
    main = appview.SearchView()
    changeroot = editPageView(regex = 'route',
                              parent = 'main',
                              form = PageForm)
    change = editPageView(regex = '(?P<path>[\w./-]*)', splitregex = False,
                          parent = 'changeroot',
                          form = PageForm)
    
    def get_object(self, request, **kwargs):
        url = '/'
        if 'path' in kwargs:
            url += kwargs['path']
        return self.mapper.get(url = url)
    
    def underlying(self, djp):
        path = djp.kwargs.get('path','')
        site,view,kwargs = djp.site.resolve(path)
        return view(djp.request, **kwargs)
        
    def objectbits(self, page):
        return {'path': page.url[1:]}
    