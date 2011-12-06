import sys
import json
import traceback
import logging
from functools import partial

from djpcms.utils import logtrace
from djpcms.html import Widget, WidgetMaker

from .http import Response, STATUS_CODE_TEXT, UNKNOWN_STATUS_CODE

logger = logging.getLogger('djpcms')

__all__ = ['HtmlPage','Meta','html_choices','htmldoc','htmldefaultdoc']


htmldefaultdoc = 5

_Meta = WidgetMaker(tag='meta',
                    inline=True,
                    attributes=('content', 'http-equiv', 'name', 'charset'))

def Meta(*args,**kwargs):
    return Widget(_Meta,*args,**kwargs)


class HTMLdoc(object):
    
    def __init__(self, typ, name, html, vimg = None, slash = ""):
        self.typ = typ
        self.name = name
        self.html = html
        self.vimg = vimg
        self.slash = slash
        
    def meta(self, request):
        settings = request.view.settings
        if self.typ == 5:
            yield Meta(charset = settings.DEFAULT_CHARSET)
        else:
            yield Meta(content = 'text/html; charset='+\
                    settings.DEFAULT_CHARSET).attr('http-equiv','content-type')
        #yield Meta(content = settings.LANGUAGE_CODE)\
        #                .addAttr('http-equiv','content-language')

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


class HtmlPage(object):
    errorhtml = {
    404:
    "<p>Permission Denied</p>",
    404:
    "<p>Whoops! We can't find what you are looking for, sorry.</p>",
    500:
    "<p>Whoops! Server error. Something did not quite work right, sorry.</p>"}
    def __init__(self, body_renderer = None, error_renderer = None, errorhtml = None):
        if body_renderer:
            self.body_renderer = body_renderer
        if error_renderer:
            self.error_renderer = error_renderer
        self.errorhtml = self.errorhtml.copy()
        self.errorhtml.update(errorhtml or {})
    
    def _stream(self, request, body_renderer, context):
        body_renderer = body_renderer or self.body_renderer
        body = body_renderer(request, context)
        media = request.media
        page = request.page
        doc = htmldoc(None if not page else page.doctype)
        yield doc.html+'\n<head>'
        for meta in self.meta(request, doc):
            yield meta.render()
        title = context.get('title')
        if title:
            yield '<title>'+title+'</title>'
        if page:
            for h in page.additional_head:
                yield h
        for css in media.render_css:
            yield css
        yield '</head>'
        body_class = context.get('body_class')
        if body_class:
            yield "<body class='{0}'>".format(body_class)
        else:
            yield '<body>'
        yield body
        yield media.all_js
        yield self.page_script(request)
        yield '</body>\n</html>'
        
    def render(self, request, context, body_renderer = None):
        '''render a page and return a binary string'''
        page = request.page
        context['htmldoc'] = doc = htmldoc(None if not page else page.doctype)
        context = request.view.site.context(context, request)
        callback = partial(self.encode,request,body_renderer)
        return request.view.response(context, callback)
    
    def render_to_response(self, request, context, body_renderer = None,
                           content_type = None):
        settings = request.view.settings
        status = context.get('status_code',200)
        content = self.render(request, context, body_renderer)
        return Response(status = status,
                        content = content,
                        content_type = content_type or 'text/html',
                        encoding = settings.DEFAULT_CHARSET)
        
    def error_to_response(self, request, status, content_type = None):
        context = {'status_code':status}
        if not content_type and request.is_xhr:
            content_type = 'application/javascript'
        return self.render_to_response(request,
                                       context,
                                       self.error_renderer,
                                       content_type)
    
    def encode(self, request, body_renderer, context):
        text = '\n'.join(self._stream(request, body_renderer, context))
        charset = request.view.settings.DEFAULT_CHARSET
        return text.encode(charset, 'replace')
    
    def __call__(self, request, context, content_type = None):
        return self.render_to_response(request,
                                       context,
                                       content_type = content_type)
    
    def meta(self, request, doc):
        view = request.view
        charset = request.view.settings.DEFAULT_CHARSET
        for name in ('robots','description','keywords','author'):
            attr = getattr(view,'meta_'+name,None)
            if attr:
                val = attr(request)
                if val: 
                    yield Meta(name=name, content=val)
        for meta in doc.meta(request):
            yield meta
        
    def body_renderer(self, request, context):
        template_file = request.template_file
        if template_file:
            return request.view.template.render(template_file,context)
        else:
            return context.get('inner','')
        
    def error_renderer(self, request, context):
        '''The default error handler for djpcms'''
        status = context.get('status_code',500)
        title = STATUS_CODE_TEXT.get(status, UNKNOWN_STATUS_CODE)[0]
        handler = request.view
        info = request.environ.get('DJPCMS')
        if not info:
            info = djpcmsinfo(handler)
            request.environ['DJPCMS'] = info
        settings = handler.settings
        exc_info = sys.exc_info()
        # Store the stack trace in the request cache
        request.cache['exc_info'] = exc_info
        logtrace(logger, request, exc_info, status)
        inner = Widget('div', cn = 'error error{0}'.format(status))
        if settings.DEBUG:
            stack_trace = traceback.format_exception(*exc_info)
            inner.addClass('ui-state-error')
            inner.add(Widget('h2','{0} {1}'.format(status,title)))
            inner.add(Widget('h3',request.path))
            for trace in traceback.format_exception(*exc_info):
                inner.add(Widget('p',trace))
        else:
            inner.add(self.errorhtml.get(status,500))
        context.update({
            'title':title,
            'body_class': 'error',
            'stack_trace':stack_trace,
            'inner':inner.render(request)})
        return self.body_renderer(request,context)
    
    def page_script(self, request):
        settings = request.view.settings
        html_options = settings.HTML.copy()
        html_options.update({'debug':settings.DEBUG,
                             'media_url': settings.MEDIA_URL})
        return '''\
<script type="text/javascript">
(function($) {
    $(document).ready(function() {
        $.djpcms.set_options(%s);
        $(document).djpcms().trigger('djpcms-loaded');
    });
}(jQuery));
</script>''' % json.dumps(html_options)

