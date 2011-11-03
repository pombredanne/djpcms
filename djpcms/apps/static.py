'''\
Dependcies: ``None``

Useful application for serving static files during development.

It also provides several utilities for fetching external media.
'''
import os
import re
import stat
import mimetypes
from email.utils import parsedate_tz, mktime_tz

from djpcms import views, http
from djpcms.utils.importer import import_module

# Third party application list.
third_party_applications = []

_media = None


class pathHandler(object):
    
    def __init__(self, name, path, mediadir):
        self.name     = name
        self.base     = path
        self.mpath    = os.path.join(path,mediadir)
        self.absolute_path = os.path.join(self.mpath,name)
        self.exists   = os.path.exists(self.mpath)
        self.url = '/{0}/{1}/'.format(mediadir,name)


class DjangoAdmin(object):
    '''A django admin static application'''
    def check(self, app):
        return app.startswith('django.')
    
    def handler(self, app):
        if app == 'django.contrib.admin':
            return self
        
    def __call__(self, name, path, mediadir):
        h = pathHandler(name,path,mediadir)
        h.absolute_path = h.mpath
        return h

third_party_applications.append(DjangoAdmin())


def application_map(applications, safe = True):
    '''Very very useful function for finding static media directories.
It looks for the ``media`` directory in each installed application.'''
    map = {}
    mediadir = 'media'
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
            if not safe:
                raise
            continue

        h = handler(name,module.__path__[0],mediadir)
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
            html = site.template.render(appmodel.template,
                                {'names':sorted(mapping),
                                 'files':[],
                                 'directory':directory,
                                 'notroot':notroot})
            html = html.encode('latin-1','replace')
            return http.Response(html, content_type = 'text/html')
        else:
            raise http.Http404


class StaticFileView(StaticView):
    DEFAULT_CONTENT_TYPE = 'application/octet-stream'
    
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
        html = self.site.template.render(self.appmodel.template,
                             {'names':names,
                              'files':files,
                              'directory':request.path,
                              'notroot':True})
        html = html.encode('latin-1','replace')
        return http.Response(html, content_type = 'text/html')
        
    def serve_file(self, request, fullpath):
        # Respect the If-Modified-Since header.
        statobj = os.stat(fullpath)
        mimetype, encoding = mimetypes.guess_type(fullpath)
        mimetype = mimetype or self.DEFAULT_CONTENT_TYPE
        if not self.was_modified_since(request.environ.get(
                                            'HTTP_IF_MODIFIED_SINCE',None),
                                       statobj[stat.ST_MTIME],
                                       statobj[stat.ST_SIZE]):
            return http.Response(status = 304,
                                 content_type=mimetype,
                                 encoding = encoding)
        contents = open(fullpath, 'rb').read()
        response = http.Response(contents,
                                 content_type=mimetype,
                                 encoding = encoding)
        response.headers["Last-Modified"] =\
                         http.http_date(statobj[stat.ST_MTIME])
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
            settings = site.settings
            mapping = appmodel.loadapps(site)
            name = settings.FAVICON_MODULE or settings.SITE_MODULE
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
    '''Simply add FavIcon() to your urls to serve the favicon.'''
    main = FavIconView(append_slash = False)
    
    def __init__(self, *args, **kwargs):
        super(FavIcon,self).__init__('/favicon.ico',*args,**kwargs)

