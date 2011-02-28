import os
import re
import stat
import mimetypes
from email.utils import parsedate_tz, mktime_tz

from djpcms.views import appview, appsite
from djpcms.utils.importer import import_module
from djpcms.utils.http import http_date
from djpcms.template import loader


class pathHandler(object):
    
    def __init__(self, name, path, mediadir = 'media'):
        self.name     = name
        self.base     = path
        self.mpath    = os.path.join(path,mediadir)
        self.absolute_path = os.path.join(self.mpath,name)
        self.exists   = os.path.exists(self.mpath)


class StaticFileView(appview.View):
    
    def __init__(self, show_indexes=False, **kwargs):
        self.show_indexes = show_indexes
        super(StaticFileView,self).__init__(**kwargs)


class StaticFileRoot(StaticFileView):        
    
    def __call__(self, request, **kwargs):
        appmodel = self.appmodel
        mapping = appmodel.loadapps(request.site)
        http = request.site.http
        directory = request.path
        notroot = directory != '/'
        if appmodel.show_indexes:
            html = loader.render(appmodel.template,
                                {'names':sorted(mapping),
                                 'files':[],
                                 'directory':directory,
                                 'notroot':notroot})
            return http.HttpResponse(html, mimetype = 'text/html')
        else:
            raise request.http.Http404


class StaticFileApp(StaticFileView):
    
    def __call__(self, request, **kwargs):
        appmodel = self.appmodel
        http = request.site.http
        mapping = appmodel.loadapps(request.site)
        paths = kwargs['path'].split('/')
        app = paths.pop(0)
        if app in mapping:
            hd = mapping[app]
            fullpath = os.path.join(hd.absolute_path,*paths)
            if os.path.isdir(fullpath):
                if appmodel.show_indexes:
                    return self.directory_index(request, fullpath)
                else:
                    raise http.Http404
            elif os.path.exists(fullpath):
                return self.serve_file(request, fullpath)
            else:
                raise http.Http404
        else:
            raise http.Http404
        
    def directory_index(self, request, fullpath):
        files = []
        names = []
        for f in sorted(os.listdir(fullpath)):
            if not f.startswith('.'):
                if os.path.isdir(os.path.join(fullpath, f)):
                    names.append(f)
                else:
                    files.append(f)
        html = loader.render(self.appmodel.template,
                             {'names':names,
                              'files':files,
                              'directory':request.path})
        return request.site.http.HttpResponse(html,
                                              mimetype = 'text/html')
        
    def serve_file(self, request, fullpath):
        http = request.site.http
        # Respect the If-Modified-Since header.
        statobj = os.stat(fullpath)
        mimetype, encoding = mimetypes.guess_type(fullpath)
        mimetype = mimetype or 'application/octet-stream'
        if not self.was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                                       statobj[stat.ST_MTIME],
                                       statobj[stat.ST_SIZE]):
            return http.HttpResponse(status = 304,
                                     mimetype=mimetype)
        contents = open(fullpath, 'rb').read()
        response = http.HttpResponse(contents,
                                     mimetype=mimetype)
        http.set_header(response, "Last-Modified", http_date(statobj[stat.ST_MTIME]))
        http.set_header(response, "Content-Length", len(contents))
        if encoding:
            http.set_header(response, "Content-Encoding", encoding)
        return response
    
    def was_modified_since(self, header=None, mtime=0, size=0):
        """
        Was something modified since the user last downloaded it?
    
        header
          This is the value of the If-Modified-Since header.  If this is None,
          I'll just return True.
    
        mtime
          This is the modification time of the item we're talking about.
    
        size
          This is the size of the item we're talking about.
        """
        try:
            if header is None:
                raise ValueError
            matches = re.match(r"^([^;]+)(; length=([0-9]+))?$", header,
                               re.IGNORECASE)
            header_mtime = mktime_tz(parsedate_tz(matches.group(1)))
            header_len = matches.group(3)
            if header_len and int(header_len) != size:
                raise ValueError
            if mtime > header_mtime:
                raise ValueError
        except (AttributeError, ValueError, OverflowError):
            return True
        return False



class Static(appsite.Application):
    '''A simple application for handling static files.
    This application should be only used during development while
    leaving the task of serving media files to other servers in production.'''
    _media = None
    site_name = 'site'
    show_indexes = False
    template = ['static_index.html','djpcms/static_index.html']
    main = StaticFileRoot()
    app  = StaticFileApp(parent = 'main', regex = '(?P<path>[\w./-]*)', append_slash = False)
    
    def __init__(self, *args, **kwargs):
        self.show_indexes = kwargs.pop('show_indexes',self.show_indexes)
        super(Static,self).__init__(*args,**kwargs)
    
    def loadapps(self, site):
        '''Load application media.'''
        if self._media is None:
            self._media = mapping = {}
            for app in site.settings.INSTALLED_APPS:
                sapp = app.split('.')
                name = sapp[-1]
                if app.startswith('django.'):
                    # we skip any django contrib application
                    continue
                else:
                    handler = pathHandler
                
                try:
                    module = import_module(app)
                except ImportError:
                    continue
    
                hd = handler(name,module.__path__[0])
                if hd.exists:
                    mapping[name] = hd
            if self.site_name:
                hd = handler(self.site_name,site.settings.SITE_DIRECTORY)
                if hd.exists:
                    mapping[self.site_name] = hd
                
                
        return self._media
    