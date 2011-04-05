from djpcms import views

from .layout import HtmlReportForm



class WritingApplication(views.ModelApplication):
    form = HtmlReportForm
    search = views.SearchView()
    add = views.AddView(regex = 'write')
    view = views.ViewView(regex = '(?P<slug>{0})'.format(views.SLUG_REGEX))
    change = views.ChangeView(regex = 'change'.format(views.SLUG_REGEX))
    
    def objectbits(self, instance):
        return {'slug':instance.slug}
    
    def get_object(self, request, **kwargs):
        try:
            slug = kwargs.get('slug',None)
            return self.mapper.get(slug = slug)
        except:
            return None 