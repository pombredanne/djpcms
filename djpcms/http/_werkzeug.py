from werkzeug import wrappers
from werkzeug import exceptions
from werkzeug.serving import run_simple

from djpcms import sites
from djpcms.core.exceptions import HttpException


Request = wrappers.Request
HttpResponse = wrappers.Response
Http404 = exceptions.NotFound


def make_request(environ):
    request = Request(environ)
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