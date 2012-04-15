import sys
import re
import logging

from djpcms.core.exceptions import Http404, HttpException, PermissionDenied
from djpcms.core.tree import DjpcmsTree, BadNode
from djpcms.utils import logtrace

from .profiler import profile_response
from .wrappers import make_request, Response, ResponseRedirect


logger = logging.getLogger('djpcms')


__all__ = ['WSGI','WSGIhandler']


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
        for i,middleware in enumerate(self.middleware):
            try:
                response = middleware(environ, start_response)
            except:
                if i < len(self.middleware):
                    logger.critical('Critical error while processing request '\
                                    'middleware', exc_info=True)
                else:
                    raise
            if response is not None:
                for rm in self.response_middleware:
                    try:
                        rm(environ, start_response, response)
                    except:
                        logger.critical('Critical error while processing '\
                                        'response middleware', exc_info=True)
                response(environ, start_response)
                return response
        #raise RuntimeError('Could not obtain response')
        return ()

    
class WSGI(object):
    '''WSGI handler. It looks for application site and
delegate the handling to them.'''
    def __init__(self, site):
        self.site = site
        self.error = site.response.error_to_response
        
    @property
    def route(self):
        return self.site.route
    
    def __str__(self):
        return self.site.path
    
    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,self)
        
    def __call__(self, environ, start_response):
        cleaned_path = clean_path(environ)
        if cleaned_path is not None:
            return cleaned_path
        query = environ.get('QUERY_STRING','')
        PK = self.site.settings.PROFILING_KEY
        if PK and PK in query:
            return profile_response(environ, start_response, self._handle)
        else:
            return self._handle(environ, start_response)
        return response
        
    def _handle(self, environ, start_response):
        tree = self.page_tree()
        try:
            node = tree.resolve(environ['PATH_INFO'])
        except Http404 as e:
            if e.trypath:
                return ResponseRedirect(e.trypath)
            else:
                req = make_request(environ, BadNode(tree,
                                                    e.handler or self.site))
                return self.error(req, 404)
            
        request = None
        try:
            request = make_request(environ, node, safe = False)
            if request.method not in request.methods():
                raise HttpException(status = 405,
                    msg = 'method {0} is not allowed'.format(request.method))
            elif not request.has_permission():
                raise PermissionDenied()
            return request.view(request)
        except Exception as e:
            if request is None:
                request = make_request(environ, node)
            status = getattr(e, 'status', 500)
            logtrace(logger, request, True, status)
            return self.error(request, status)
        
    def page_tree(self):
        Page = self.site.Page
        tree = self.site.tree
        if Page:
            return DjpcmsTree(tree, Page.query())
        else:
            return DjpcmsTree(tree)
