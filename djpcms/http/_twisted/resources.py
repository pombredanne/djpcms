import os
import logging

from zope.interface import implements

from twisted.internet import defer
from twisted.web import resource, server, wsgi, static
from twisted.internet.error import CannotListenError
from twisted.web.resource import IResource

from unuk.core import exceptions


logger = logging.getLogger('txweb')


class Root(resource.Resource):
    
    def __init__(self, service, application):
        resource.Resource.__init__(self)
        self.service = service
        
    def getChild(self, path, request):
        path0 = request.prepath.pop(0)
        request.postpath.insert(0, path0)
        return self.service


class Favicon(object):
    isLeaf = True
    
    favicon = "\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
    def __init__(self, favicon):
        self.favfile = favicon
        
    def render(self, request):
        request.setHeader("Content-Type","image/gif")
        if os.path.exists(self.favfile):
            favicon = open(self.favfile,'r').read()
        else:
            favicon = self.favicon
        request.write(favicon)


class TwistedResource(object):
    '''An IResource implementation which delegates responsibility
for all resources hierarchically inferior to it

:param appserver: server object
:param reactor: An twistyed reactor which will be passed on to
                RPC response to schedule calls in the I/O thread.
:param pool: A :class:`unuk.concurrency.ConncurrencyPool` instance or ``None``.
:param application: the RPC application object.'''
    implements(IResource)
    
    isLeaf = True
    
    def __init__(self, server, reactor, pool):
        self.server   = server
        self._reactor = reactor
        self._pool    = pool
        self.handler  = server.handler
    
    def render(self, request):
        handler  = self.handler.get_handler(request.path)
        if not handler:
            raise Exception
        response = getattr(self,'{0}_response'.format(handler.serve_as))
        return response(handler, request)

    def wsgi_response(self, handler, request):
        resource = wsgi.WSGIResource(self._reactor, self._pool, self.handler)
        return resource.render(request)
        
    def jsonrpc_response(self, handler, request):
        response = _RPCResponse(self._pool, handler, request)
        response.start()
        return server.NOT_DONE_YET
        
                
class _RPCResponse(object):
    _requestFinished = False
    
    def __init__(self, pool, application, request):
        self.started = False
        self.pool    = pool
        self.application = application
        self.request = request
        self.request.notifyFinish().addBoth(self._finished)
    
    @property
    def logger(self):
        return self.application.logger
    
    def _finished(self, ignored):
        """
        Record the end of the response generation for the request being
        serviced.
        """
        self._requestFinished = True
        
    def start(self):
        if self.pool:
            self.pool.dispatch(self.run)
        else:
            self.run()
        
    def run(self):
        request = self.request
        request.content.seek(0, 0)
        content = request.content.read()
        rpc     = self.application
        method, args, kwargs, id, version = rpc.get_method_and_args(content)
        if not method:
            self._cbRender(exceptions.InvalidRequest('Method not available'),
                           request, None, id, version)
        try:
            function = rpc._getFunction(method)
        except exceptions.Fault as f:
            self._cbRender(f, request, None, id, version)
        else:
            rpc.logger.debug('invoking function %s' % method)
            request.setHeader("content-type", "text/json")
            d = defer.maybeDeferred(function, rpc, request, *args, **kwargs)
            d.addErrback(self._ebRender,
                         request,
                         function,
                         id,
                         version)
            d.addCallback(self._cbRender,
                          request,
                          function,
                          id,
                          version)
        return server.NOT_DONE_YET

    def _cbRender(self, result, request, function, id, version):
        '''Render success result
        '''
        if id:
            dumps = self.application.dumps
            try:
                s = dumps(id, version, result = result)
            except:
                f = exceptions.InternalError("can't serialize output")
                s = dumps(id, version, error = f)
            request.setHeader("content-length", str(len(s)))
            request.write(s)
        request.finish()

    def _ebRender(self, failure, request, function, id, version):
        if id:
            dumps = self.application.dumps
            try:
                s = dumps(id, version, error = failure.value)
            except:
                f = exceptions.InternalError("can't serialize output")
                s = dumps(id, version, error = f)
            request.setHeader("content-length", str(len(s)))
            request.write(s)
        request.finish()
    
    def getChildWithDefault(self, name, request):
        raise RuntimeError("Cannot get IResource children from WSGIResource")

    def putChild(self, path, child):
        raise RuntimeError("Cannot put IResource children under WSGIResource")


def builserver(self, reactor):
    '''Build twisted web server'''
    pool = self.pool
    port = self._port
    self.service = TwistedResource(self, reactor, pool)
    self.root = Root(self.service, self)
    main_site = server.Site(self.root)
    secure = self.secure
    if pool and not pool.started:
        pool.start()
    if secure:
        try:
            from twisted.internet import ssl
        except:
            raise ValueError('OpenSSL library not available. Cannot use ssl.')
    try:
        if secure:
            p = reactor.listenSSL(port,
                                  main_site,
                                  ssl.DefaultOpenSSLContextFactory(*secure))
        else:
            p = reactor.listenTCP(port, main_site)
        self.socket = p.socket
        self.port   = p._realPortNumber
    except CannotListenError as e:
        self.stop()
        logger.error('%s' % e)
        raise
    logger.debug('Add system events to service.')
    reactor.addSystemEventTrigger('before', 'shutdown', self.stop)
    logger.info('Listening on port %s' % self.port)
    
