from django import http
from django.core.handlers import wsgi
from django.contrib.auth import authenticate, login, logout

from djpcms.apps.handlers import DjpCmsHandler
from djpcms.core.exceptions import *

Request = wsgi.WSGIRequest

class HttpResponse(http.HttpResponse):
    
    def __init__(self, content='', status=None, content_type=None, encoding = None):
        super(HttpResponse,self).__init__(content=content, status=status, content_type=content_type)


STATUS_CODE_TEXT = wsgi.STATUS_CODE_TEXT


def from_data_dict(data):
    for key,val in data.iterlists():
        if key.endswith('[]'):
            key = key[:-2]
            if not isinstance(key,(list,tuple)):
                val = [val]
            yield key,val
        if len(val) > 1:
            yield key,val
        else:
            yield key,val[0]

def make_request(environ):
    request = Request(environ)
    request.is_xhr = request.is_ajax()
    if request.method == 'POST':
        data = request.POST
    else:
        data = request.GET
    request.data_dict = dict(from_data_dict(data))
    return request
    

def set_header(self, key, value):
    self[key] = value


def delete_test_cookie(request):
    request.delete_test_cookie()
    
    
def path_with_query(request):
    path = request.path
    if request.method == 'GET':
        qs =  request.environ['QUERY_STRING']
        if qs:
            return path + '?' + qs
    return path


def finish_response(res, environ, start_response):
    try:
        status_text = STATUS_CODE_TEXT[res.status_code]
    except KeyError:
        status_text = 'UNKNOWN STATUS CODE'
    status = '%s %s' % (res.status_code, status_text)
    response_headers = [(str(k), str(v)) for k, v in res.items()]
    for c in res.cookies.values():
        response_headers.append(('Set-Cookie', str(c.output(header=''))))
    if start_response is not None:
        start_response(status, response_headers)
    return res
        

def serve(port = 0, sites = None, use_reloader = False):
    from django.core.servers.basehttp import run
    run('localhost', port, DjpCmsHandler(sites))
    
