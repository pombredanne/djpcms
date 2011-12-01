import sys
import re
import traceback
import logging

from djpcms.core.exceptions import Http404, HttpException, PermissionDenied 
from djpcms.utils import logtrace

from .profiler import profile_response
from .wrappers import Request, Response, ResponseRedirect,\
                         STATUS_CODE_TEXT, UNKNOWN_STATUS_CODE
from .cache import djpcmsinfo


logger = logging.getLogger('djpcms')


__all__ = ['WSGI','WSGIhandler','standard_exception_handle']


def clean_path(environ):
    '''Clean url and redirect if needed
    '''
    path = environ['PATH_INFO']
    if '//' in path:
        url = re.sub("/+" , '/', path)
        if not url.startswith('/'):
            url = '/%s' % url
        qs = environ['QUERY_STRING']
        if qs and environ['method'] == 'GET':
            url = '{0}?{1}'.format(url,qs)
        return ResponseRedirect(url)


class WSGIhandler(object):
    
    def __init__(self, middleware, response_middleware = None):
        self.middleware = middleware
        self.response_middleware = response_middleware or []
        
    def __call__(self, environ, start_response):
        '''The WSGI callable'''
        #request = self.REQUEST(environ)
        for middleware in self.middleware:
            response = middleware(environ, start_response)
            if response is not None:
                for rm in self.response_middleware:
                    rm(environ, start_response, response)
                response(environ, start_response)
                return response
        return ()

    
class WSGI(object):
    '''WSGI handler. It looks for application site and
delegate the handling to them.'''
    def __init__(self, site):
        self.site = site
        self.error = site.internals['errors']
        
    @property
    def route(self):
        return self.site.route
    
    def __str__(self):
        return self.route
    
    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,self)
        
    def __call__(self, environ, start_response):
        cleaned_path = clean_path(environ)
        if cleaned_path is not None:
            return cleaned_path
        settings = self.site.settings
        if settings.PROFILING_KEY:
            return profile_response(environ,
                                    start_response,
                                    self.site,
                                    settings.PROFILING_KEY,
                                    self._handle,
                                    settings)
        else:
            return self._handle(environ, start_response)
        return response
        
    def _handle(self, environ, start_response):
        try:
            view, urlargs = self.site.resolve(environ['PATH_INFO'][1:])
        except Http404 as e:
            if e.trypath:
                return ResponseRedirect(e.trypath)
            else:
                return self.error(Request(environ,e.handler or self.site), 404)
            
        environ['DJPCMS'] = djpcmsinfo(view, urlargs)
        request = Request(environ, view, urlargs)
        try:
            if request.method not in view.methods(request):
                raise HttpException(status = 405,
                    msg = 'method {0} is not allowed'.format(request.method))
            elif not request.has_permission():
                raise PermissionDenied()
            return view(request)
        except Exception as e:
            return self.error(request, getattr(e,'status',500))
        

def standard_exception_handle(request, status):
    '''The default error handler for djpcms'''
    handler = request.view
    info = request.environ.get('DJPCMS')
    if not info:
        info = djpcmsinfo(handler)
        request.environ['DJPCMS'] = info
    settings = handler.settings
    exc_info = sys.exc_info()
    template = '{0}.html'.format(status)
    template2 = 'errors/' + template
    template3 = 'djpcms/' + template2
    
    logtrace(logger, request, exc_info, status)
    #store stack trace in the DJPCMS environment variable
    info['stack_trace'] = traceback.format_exception(*exc_info)
    stack_trace = '<p>{0}</p>'.format('</p>\n<p>'.join(info['stack_trace']))
    ctx = {'status':status,
           'status_text':STATUS_CODE_TEXT.get(status, UNKNOWN_STATUS_CODE)[0],
           'stack_trace':stack_trace,
           'settings':settings}
    html = handler.template.render(
                (template,template2,template3,'djpcms/errors/error.html'),
                 ctx,
                 request = request,
                 encode = 'latin-1',
                 encode_errors = 'replace')
    return Response(status = status,
                    content = html,
                    content_type = 'text/html',
                    encoding = settings.DEFAULT_CHARSET)
