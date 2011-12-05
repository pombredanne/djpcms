from .base import Widget, WidgetMaker

_Meta = WidgetMaket(tag='meta',
                    inline=True,
                    attributes=('content','http-equiv','name', 'charset'))

def Meta(*args,**kwargs):
    return Widget(_Meta,*args,**kwargs)


htmldocs = (
            (1, 
             HTMLdoc('HTML 4.01',
    """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN
http://www.w3.org/TR/html4/strict.dtd">""",
                     "valid-html401",
                     '',
                     None)),
            (2, 
             HTMLdoc('HTML 4.01 Transitional',
    """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN
http://www.w3.org/TR/html4/loose.dtd">""",
                     "valid-html401")),
            (3, 
             HTMLdoc('XHTML 1.0 Strict',
                     """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">""",
                     "valid-xhtml10",
                     "/",
                     None)),
            (4, 
             HTMLdoc('XHTML 1.0 Transitional',
    """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN
http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">""",
                     "valid-xhtml10",
                     "/",
                     """<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<meta http-equiv="Content-Language" content="en-uk" />""")),
            (5, 
             HTMLdoc('HTML5',
                     """<!DOCTYPE html>\n<html>""",
                     None,
                     None,
                     Meta(charset = "utf-8")),
            )
            )


_htmldict = dict(((h[0],(h[0],)+h[1]) for h in htmldocs))

html_choices = tuple(((t[0],t[1].name) for t in htmldocs))


class HtmlPage(object):

    def __init__(self, typ):
        d = _htmldict.get(typ,5)
        self.type, self.name, self.top, self.vimg, self.slash, self._meta = \
        _htmldict.get(typ,5)
    
    def render(self, request, context):
        media = request.media
        page = request.page
        if self.top:
            yield self.top
        yield '<head>'
        for meta in self.meta(request):
            yield meta
        yield '<title>'+request.title+'</title>'
        if page:
            for h in page.additional_head:
                yield h
        for css in request.media.render_css:
            yield css
        yield '</head>'
        yield '<body>'
        yield request.view.html_body(request)
        yield media.all_js
        yield self.page_script(request)
        yield '</body>'
        yield '</html>'
        
    def meta(self, request):
        for m in self._meta:
            yield m
        view = request.view
        for name in ('robots','description','keywords'):
            attr = view.getattr(view,'meta_'+name,None)
            if attr:
                attr = attr(request)
            if attr:
                yield Meta(name=name,content=attr)
        
    def html_body(self, request, context):
        return '{0[inner]}'.format(context)
        
    def page_script(self, request):
        settings = request.view.settings
        html_options = settings.HTML.copy()
        html_options.update({'debug':settings.DEBUG,
                             'media_url': settings.MEDIA_URL})
        return '''\
<script type="text/javascript">
(function($) {
    $(document).ready(function() {
        $.djpcms.set_options({0});
        $(document).djpcms().trigger('djpcms-loaded');
    });
}(jQuery));
</script>'''.format(html_options)
