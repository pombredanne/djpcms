from djpcms.cms.plugins.apps import RenderObject


class Text(RenderObject):
    '''The text plugin allows to write content in a straightforward manner.
You can use several different markup languages or simply raw HTML.'''
    name = "text"
    description = "Html"
    
    def for_model(self, request):
        return request.view.root.internals.get('SiteContent')
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return ''