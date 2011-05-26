'''\
Dependcies: **None**

Useful application for serving static files.
Useful during development.
'''
import os
import re
import stat
import mimetypes
from email.utils import parsedate_tz, mktime_tz

from djpcms import views, http
from djpcms.utils.importer import import_module
from djpcms.template import loader

# Third party application list.
third_party_applications = []

_media = None

class pathHandler(object):
    
    def __init__(self, name, path, mediadir = 'media'):
        self.name     = name
        self.base     = path
        self.mpath    = os.path.join(path,mediadir)
        self.absolute_path = os.path.join(self.mpath,name)
        self.exists   = os.path.exists(self.mpath)


class DjangoAdmin(object):
    '''A django admin static application'''
    def check(self, app):
        return app.startswith('django.')
    
    def handler(self, app):
        if app == 'django.contrib.admin':
            return self
        
    def __call__(self, name, path):
        h = pathHandler(name,path)
        h.absolute_path = h.mpath
        return h

third_party_applications.append(DjangoAdmin())


def application_map(applications):
    '''Very very useful function for finding static media directories.
It looks for the ``media`` directory in each installed application.'''
    map = {}
    for app in applications:
        processed = False
        for tp in third_party_applications:
            if tp.check(app):
                processed = True
                handler = tp.handler(app)
                break
        
        if not processed:
            handler = pathHandler
        
        if not handler:
            continue
        
        sapp = app.split('.')
        name = sapp[-1]
            
        try:
            module = import_module(app)
        except:
            continue

        h = handler(name,module.__path__[0])
        if h.exists:
            map[name] = h
    return map


class StaticView(views.View):
    
    def __init__(self, show_indexes=False, **kwargs):
        self.show_indexes = show_indexes
        super(StaticView,self).__init__(**kwargs)


class StaticRootView(StaticView):        
    
    def __call__(self, request, **kwargs):
        appmodel = self.appmodel
        site = self.site
        mapping = appmodel.loadapps(site)
        directory = request.path
        notroot = directory != '/'
        if appmodel.show_indexes:
            html = loader.render(appmodel.template,
                                {'names':sorted(mapping),
                                 'files':[],
                                 'directory':directory,
                                 'notroot':notroot})
            return http.Response(html,content_type = 'text/html')
        else:
            raise http.Http404


class StaticFileView(StaticView):
    
    def __call__(self, request, **kwargs):
        appmodel = self.appmodel
        site = self.site
        mapping = appmodel.loadapps(site)
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
                raise http.Http404('No file "{0}" in application "{1}".\
 Could not render {1}'.format(paths,app))
        else:
            raise http.Http404('Static application "{0}" not available.\
 Could not render "{1}"'.format(app,paths))
        
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
                              'directory':request.path,
                              'notroot':True})
        return http.Response(html, content_type = 'text/html')
        
    def serve_file(self, request, fullpath):
        # Respect the If-Modified-Since header.
        statobj = os.stat(fullpath)
        mimetype, encoding = mimetypes.guess_type(fullpath)
        mimetype = mimetype or 'application/octet-stream'
        if not self.was_modified_since(request.environ.get('HTTP_IF_MODIFIED_SINCE',None),
                                       statobj[stat.ST_MTIME],
                                       statobj[stat.ST_SIZE]):
            return http.Response(status = 304,
                                 content_type=mimetype,
                                 encoding = encoding)
        contents = open(fullpath, 'rb').read()
        response = http.Response(contents,
                                 content_type=mimetype,
                                 encoding = encoding)
        response.set_header("Last-Modified", http.http_date(statobj[stat.ST_MTIME]))
        response.set_header("Content-Length", len(contents))
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


class FavIconView(StaticFileView):
    
    def __call__(self, request, **kwargs):
        appmodel = self.appmodel
        site = self.site
        if not kwargs:
            mapping = appmodel.loadapps(site)
            name = site.settings.SITE_MODULE
            if name in mapping:
                hd = mapping[name]
                fullpath = os.path.join(hd.absolute_path,'favicon.ico')
                return self.serve_file(request, fullpath)
        raise http.Http404


class StaticBase(views.Application):

    def loadapps(self, site):
        '''Load application media.'''
        global _media
        if _media is None:
            _media = application_map(site.settings.INSTALLED_APPS)
        return _media
    

class Static(StaticBase):
    '''A simple application for handling static files.
    This application should be only used during development while
    leaving the task of serving media files to other servers in production.'''
    hidden = True
    has_plugins = False
    show_indexes = True
    template = ['static_index.html','djpcms/static_index.html']
    main = StaticRootView()
    app  = StaticFileView(parent = 'main',
                          regex = '(?P<path>[\w./-]*)',
                          append_slash = False)
    
    def __init__(self, *args, **kwargs):
        self.show_indexes = kwargs.pop('show_indexes',self.show_indexes)
        super(Static,self).__init__(*args,**kwargs)


class FavIcon(StaticBase):
    main = FavIconView(append_slash = False)
    