from djpcms.template import make_default_inners


__all__ = ['PageMixin']

class PageMixin(object):
    
    def makepage(self, url, **kwargs):
        from djpcms.models import Page
        page = Page(url = url, **kwargs)
        page.save()
        return page
    
    def makeInnerTemplates(self):
        from djpcms.models import InnerTemplate
        '''Create Inner templates from the ``djpcms/templates/djpcms/inner`` directory'''
        make_default_inners()
        return list(InnerTemplate.objects.all())