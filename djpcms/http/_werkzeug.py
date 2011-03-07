import re

from py2py3 import urlparse

from werkzeug import wrappers
from werkzeug import exceptions
from werkzeug.urls import iri_to_uri
from werkzeug.serving import run_simple

from djpcms import sites
from djpcms.core.exceptions import *


Request = wrappers.Request
HttpResponse = wrappers.Response


absolute_http_url_re = re.compile(r"^https?://", re.I)

def build_absolute_uri(self, location):
    """Builds an absolute URI from the location and the variables available in
    this request. If no location is specified, the absolute URI is built on
    ``request.get_full_path()``.
    """
    if not location:
        location = self.get_full_path()
    if not absolute_http_url_re.match(location):
        location = urlparse.urljoin(self.host_url, location)
    return iri_to_uri(location)
    

def make_request(environ):
    request = Request(environ)
    request.build_absolute_uri = lambda url : build_absolute_uri(request,url)
    request.COOKIES = request.cookies
    request.META = request.environ
    request.FILES = request.files
    if request.method == 'POST':
        request.POST = request.form
        request.GET = {}
        request.data_dict = dict(request.form.items())
    else:
        request.POST = {}
        request.GET = {}
        request.data_dict = {}
    return request
    

def set_header(self, key, value):
    self.headers[key] = value
    

def finish_response(response, environ, start_response):
    return response(environ, start_response)


def HttpResponseRedirect(location):
    r = HttpResponse(status = 301)
    r.location = location
    return r
        

HTTPException = exceptions.HTTPException
Http404 = exceptions.NotFound



def is_authenticated(request):
    return request.user.is_authenticated()



def serve(port = 0, use_reloader = False):
    run_simple('localhost',port,sites.wsgi,use_reloader)