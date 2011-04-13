from djpcms import views
from djpcms.template import loader
from djpcms.utils import markups, mark_safe

from .layout import HtmlReportForm
from .models import flowitem



class WritingApplication(views.ModelApplication):
    view_template = 'flowrepo/writeup.html'
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
        
    def render_object(self, djp):
        instance = djp.instance
        item = flowitem(instance)
        mkp = markups.get(item.markup)
        abstract = instance.description
        body = instance.body
        if mkp:
            handler = mkp.get('handler')
            abstract = handler(abstract)
            body = handler(body)
        return loader.render(self.view_template,
                             {'title': instance.title,
                              'abstract': abstract,
                              'body':body})