from inspect import isgenerator
import sys
import json
import traceback
import logging
from functools import partial
import logging

from djpcms.utils.py2py3 import iteritems
from djpcms.html import Renderer, Widget
from djpcms.html.layout import html_stream
from djpcms.utils.async import Deferred 
from djpcms.utils.ajax import jservererror, isajax

from .http import Response, STATUS_CODE_TEXT, UNKNOWN_STATUS_CODE


logger = logging.getLogger('djpcms')


__all__ = ['async_instance', 'ResponseHandler']
   


'''wait for an asynchronous instance'''
class async_instance_callback(object):
    __slots__ = ('callable','obj','request','args','kwargs')
    
    def __init__(self, callable, obj, request, *args, **kwargs):
        self.callable = callable
        self.obj = obj
        self.request = request
        self.args = args
        self.kwargs = kwargs
    
    def __call__(self, result):
        request = self.request.for_view_args(instance = result)
        return self.callable(self.obj,request,*self.args,**self.kwargs)


def async_instance(mf):
    
    def _(self, request, *args, **kwargs):
        instance = request.instance
        if not instance or isinstance(instance,self.model):
            return mf(self, request, *args, **kwargs)
        else:
            cbk = async_instance_callback(mf,self,request,*args,**kwargs)
            return request.view.response(instance, callback = cbk)
    
    return _


class AsyncResponse(object):
    __slots__ = ('handler','response','callback','loops','async')
    def __init__(self, handler, response, callback):
        self.handler = handler
        self.response = response
        self.callback = callback
        _process = self._process
        check_async = handler.check_async
        self.loops = 0
        self.async = lambda v : check_async(_process(v))
        
    def __iter__(self):
        # release the loop if it has run already
        if self.loops:
            yield self.handler.not_done_yet()
        yield self.run()
        
    def run(self):
        '''Run the asynchronous response. If all results are available
 it return the result otherwise it return ``self``.'''
        self.loops += 1
        async, result = self.async(self.response)
        if async:
            return self
        elif self.callback:
            return self.callback(result)
        else:
            return result
    
    def _process(self, value):
        '''Recursive function for handling a potentially asynchronous *value*
        '''
        if not value:
            return value
        if isinstance(value, Deferred):
            if value.called:
                value = value.result
            return value
        
        async = self.async
        if isinstance(value,dict) and not isinstance(value,aDict):
            new_value = aDict()
            for k,val in iteritems(value):
                is_async,val = async(val)
                if is_async:
                    return val
                else:
                    new_value[k] = val
            return new_value
        #
        elif isinstance(value, Renderer):
            is_async, val = async(value.render())
            if is_async:
                return val
            else:
                value.context = val
                return value.render()
        #
        elif isgenerator(value):
            value = tuple(value)
            
        if isinstance(value, (list,tuple)) and not isinstance(value,aList):
            new_value = aList()
            for val in value:
                is_async,val = async(val)
                if is_async:
                    return val
                else:
                    new_value.append(val)
            return new_value
        #
        elif isinstance(value, AsyncResponse):
            return value.run()

        return value


class _ResponseCallback(Deferred):
    # Internal class for handling asyncronous rendering of an HTML page
    def __init__(self, handler, request):
        self.handler = handler
        self.request = request
        self.body_renderer = body_renderer
        self.response = None
    
    def __call__(self, context):
        if self.response is not None:
            return self.handler.body(self.request,
                                     self.response,
                                     context,
                                     self.body_renderer)
        else:
            return AsyncResponse(self.handler, context, self)
                 

class ResponseHandler(object):
    '''An asynchronous, fully customizable,
:ref:`response handler <response-handler>` implementation. An instance
of this class is a callable which accepts two arguments, the response to
evaluate and an optional callback function receiving as only
parameter the result from the call.
It is used to obtain synchronous results from a, potentially asynchronous,
input *response*::

    import djpcms
    
    handler = djpcms.ResponseHandler()
    
    result = handler({'bla':'foo'})
    result = handler({'bla':'foo'}, callback = lambda r : r)

    result = handler({'bla':'foo'},
                     callback = lambda r : "the value is {0[bla]}".format(r))
    
:parameter body_renderer: a function for rendering the body part of your
    html page. If provided it overrides the :meth:`body_renderer`.
    
:parameter error_renderer: a function for rendering the body part of your
    html page when an error occur. If provided it overrides the
    :meth:`error_renderer`.
    
:parameter errorhtml: overrides the :attr:`errorhtml` dictionary.


**Attributes**

.. attribute:: errorhtml

    A dictionary for mapping error status codes into html to display.
    '''
    errorhtml = {
    404:
    "<p>Permission Denied</p>",
    404:
    "<p>Whoops! We can't find what you are looking for, sorry.</p>",
    500:
    "<p>Whoops! Server error. Something did not quite work right, sorry.</p>"}
    
    def __init__(self, body_renderer = None, error_renderer = None,
                 errorhtml = None, html_streamer = None):
        if body_renderer:
            self.body_renderer = body_renderer
        if error_renderer:
            self.error_renderer = error_renderer
        self.html_streamer = html_streamer or html_stream
        self.errorhtml = self.errorhtml.copy()
        self.errorhtml.update(errorhtml or {})

    def __call__(self, response, callback = None):
        if not response:
            return response
        return AsyncResponse(self, response, callback).run()
        
    def not_done_yet(self):
        '''This function should return an element recognized by the
asynchronous engine serving your application. The element will 
cause asynchronous engine to postpone the evaluation of this response and
continue evaluating other requests.

To use djpcms in an asynchronous engine you need  to implement this function.
 '''
        raise NotImplementedError('Cannot handle Asynchronous responses')
    
    def check_async(self, value):
        if isinstance(value,AsyncResponse):
            return True,value
        else:
            return self.async(value)
        
    def async(self, value):
        '''Check if *value* is an asynchronous element. It returns a two
elements tuple containing a boolean flag and a result. If *value* is
asynchronous and its result is not yet available, the function should return::

    (True,newvalue)
     
otherwise::

    (False,newvalue)
     
where *newvalue* can be *value* or a modified version.
 
This function, like :meth:`not_done_yet` is engine dependent and
therefore should be re-implemented for different asynchronous engines.'''
        if hasattr(value,'query'):
            value = value.query
        return False,value
    
    def render_to_response(self, request, stream, status = 200):
        '''Handle a *request* *context* using a *body renderer*.
A typical usage::

    import djpcms
    
    response_handler = djpcms.ResponseHandler()
    
    ...
    
    response = response_handler.get_response(request, context)

:parameter request: an HTTP :class:`Request`.
:parameter context: a context dictionary.
:parameter body_renderer: optional callable used for rendering the
    context. If not provided, the :meth:`body_renderer` will be used.
:rtype: a :class:`Response` object'''
        if isinstance(stream, Deferred):
            if not stream.called:
                callback = partial(self._render_to_response, request)
                content = request.view.response(stream, callback)
                return Response(
                            content = request.view.response(stream, callback),
                            content_type = self.default_content_type,
                            encoding = request.settings.DEFAULT_CHARSET)
        return self._render_to_response(request, stream, status)
    
    def _render_to_response(self, request, content, status = 200):
        encoding = request.settings.DEFAULT_CHARSET
        content_type = request.settings.DEFAULT_CONTENT_TYPE
        if isajax(content):
            content_type = content.content_type()
            content = content.dumps()
        if content_type == 'text/html':
            content = '\n'.join(self.html_streamer(request, content, status))
        data = content.encode(encoding, 'replace')
        return Response(content = data,
                        content_type = content_type,
                        encoding = encoding)
    
    def error_to_response(self, request, status_code):
        '''Equivalent to :meth:`render_to_response` methods, when an error
occurs. It is equivalent to call :meth:`render_to_response` with the
following parameter::

    self.render_to_response(request, 
                            {'status_code':status_code,
                            'exc_info': sys.exc_info()},
                            self.error_renderer)
    '''
        return self.render_to_response(request,
                                       {'status_code':status_code,
                                        'exc_info': sys.exc_info()},
                                       self.error_renderer)
    
    def body(self, request, response, context, body_renderer):
        '''This is the final piece of :meth:`render_to_response`.
The context is ready to be rendered.'''
        if isajax(context):
            content = self.ajax_content(response, context)
        else:
            body_renderer = body_renderer or self.body_renderer
            response.status_code = context.get('status_code',200)
            body = body_renderer(request, context)
            if isajax(body):
                response.status_code = 200
                content = self.ajax_content(response, body)
            else:
                context['body'] = body
                content = '\n'.join(self._stream(request, context))
        return self.encode(request, content)
    
    def encode(self, request, text):
        charset = request.view.settings.DEFAULT_CHARSET
        return text.encode(charset, 'replace')
        
    def error_renderer(self, request, context):
        '''The default error renderer. It handles both ajax and
 standard responses. Override if you need to.'''
        status = context.get('status_code',500)
        exc_info = context.get('exc_info')
        title = STATUS_CODE_TEXT.get(status, UNKNOWN_STATUS_CODE)[0]
        handler = request.view
        settings = request.settings
        if exc_info and exc_info[0] is not None:
            # Store the stack trace in the request cache and log the traceback
            request.cache['traces'].append(exc_info)
        else:
            exc_info = None
        error = Widget('div', cn = 'page-error error{0}'.format(status))
        inner = error
        
        if not request.is_xhr:
            inner = Widget('div', error)
                
        if settings.DEBUG:
            error.addClass('ui-state-error')
            error.add(Widget('h2','{0} {1}'.format(status,title)))
            error.add(Widget('h3',request.path))
            if exc_info:
                for trace in traceback.format_exception(*exc_info):
                    error.add(Widget('p',trace))
        else:
            error.add(self.errorhtml.get(status,500))
            
        if request.is_xhr:
            return jservererror(request, inner.render(request))
        else:
            context.update({
                'title':title,
                'body_class': 'error',
                'content':inner.render(request)})
            return self.body_renderer(request,context)
    


