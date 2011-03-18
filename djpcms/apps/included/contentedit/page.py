from djpcms.template import loader
from djpcms.forms import HtmlForm, HtmlWidget
from djpcms import views

from .layout import HtmlPageForm 
    

class EditingPanel(HtmlWidget):
    template = 'djpcms/content/edit_panel.html'
    tag = 'div'
    
    def inner(self, djp):
        view = djp.view
        context = {'form': view.get_form(djp).render(djp)}
        return loader.render(self.template,context)
        

class editPageView(views.ChangeView):
    editing_panel = EditingPanel
    
    def get_context(self, djp):
        vdjp    = self.appmodel.underlying(djp)
        context = vdjp.view.get_context(vdjp,editing=True)
        context['page_url'] = vdjp.url
        context['editing_panel'] = self.editing_panel(cn = 'djpcms-editing').render(djp)
        context['bodybits'] = loader.mark_safe(' class="edit"')
        return context
    

class PageApplication(views.ModelApplication):
    '''Application for inline editing of pages'''
    hidden = True  
    main = views.SearchView()
    changeroot = editPageView(regex = 'route',
                              parent = 'main',
                              form = HtmlPageForm)
    change = editPageView(regex = '(?P<path>[\w./-]*)',
                          parent = 'changeroot',
                          form = HtmlPageForm)
    
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
    
