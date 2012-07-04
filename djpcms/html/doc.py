import json

from djpcms.html import Widget, WidgetMaker
from djpcms.utils.text import UnicodeMixin, ispy3k

if ispy3k:
    from http.client import responses
else:
    from httplib import responses

__all__ = ['Meta',
           'html_choices',
           'htmldoc',
           'htmldefaultdoc',
           'html_doc_stream',
           'error_title']


htmldefaultdoc = 5

_Meta = WidgetMaker(tag='meta',
                    inline=True,
                    attributes=('content', 'http-equiv', 'name', 'charset'))

error_title = lambda status : responses.get(\
                                status,'Unknown error {0}'.format(status))

def Meta(*args,**kwargs):
    return Widget(_Meta,*args,**kwargs)


class HTMLdoc(UnicodeMixin):
    
    def __init__(self, typ, name, html, vimg = None, slash = ""):
        self.typ = typ
        self.name = name
        self.html = html
        self.vimg = vimg
        self.slash = slash
        
    def __unicode__(self):
        return self.name
    
    def meta(self, name, value):
        if value:
            if name == 'charset':
                if self.typ == 5:
                    return Meta(charset = value)
                else:
                    return Meta(content = 'text/html; charset='+value)\
                                .attr('http-equiv','content-type')
            else:
                return Meta(name = name, content = value)
                        

htmldocs = (
            (1, 
             HTMLdoc(1,'HTML 4.01',
    """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN
http://www.w3.org/TR/html4/strict.dtd">""",
                     "valid-html401")),
            (2, 
             HTMLdoc(2,'HTML 4.01 Transitional',
    """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN
http://www.w3.org/TR/html4/loose.dtd">""",
                     "valid-html401")),
            (3, 
             HTMLdoc(3,'XHTML 1.0 Strict',
                     """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">""",
                     "valid-xhtml10",
                     "/")),
            (4, 
             HTMLdoc(4,'XHTML 1.0 Transitional',
    """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN
http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">""",
             "valid-xhtml10",
             "/",
             )),
            (5, 
             HTMLdoc(5,'HTML5',
                     """<!DOCTYPE html>\n<html>"""),
            )
            )


_htmldict = dict(((h[0],h[1]) for h in htmldocs))

html_choices = tuple(((t[0],t[1].name) for t in htmldocs))


def htmldoc(code = None):
    global _htmldict, htmldefaultdoc
    code = code or htmldefaultdoc
    if code in _htmldict:
        return _htmldict[code]
    else:
        return _htmldict[htmldefaultdoc]


meta_default = lambda r : None


def html_doc_stream(request, stream, status=200):
    media = request.media
    view = request.view
    settings = view.settings
    page = request.page
    doc = htmldoc(None if not page else page.doctype)
    #
    # STARTS HEAD
    yield doc.html+'\n<head>'
    if status == 200:
        body_class = view.get_body_class(request)
        title = request.title
    else:
        body_class = settings.HTML.get('error')
        title = error_title(status)
    for name in settings.META_TAGS:
        value = getattr(view, 'meta_'+name, meta_default)(request)
        meta = doc.meta(name, value)
        if meta is not None:
            yield meta.render()
    if title:
        yield '<title>'+title+'</title>'
    if page:
        for h in page.additional_head:
            yield h
    for css in media.render_css:
        yield css
    yield '</head>'
    # ENDS HEAD
    if body_class:
        yield "<body class='{0}'>".format(body_class)
    else:
        yield '<body>'
    if not isinstance(stream, (list,tuple)):
        yield stream
    else:
        for s in stream:
            yield s
    js = media.all_js
    if js:
        yield js
        yield page_script(request)
    yield '</body>\n</html>'
    
    
def page_script(request):
        settings = request.view.settings
        html_options = settings.HTML.copy()
        html_options.update({'debug':settings.DEBUG,
                             'media_url': settings.MEDIA_URL})
        on_document_ready = '\n'.join(request.on_document_ready)
        return '''\
<script type="text/javascript">
(function($) {
    $(document).ready(function() {
        $.djpcms.set_options(%s);
        $(document).djpcms().trigger('djpcms-loaded');
        %s
    });
}(jQuery));
</script>''' % (json.dumps(html_options),on_document_ready)