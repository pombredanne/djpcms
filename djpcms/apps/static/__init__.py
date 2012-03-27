'''\
Useful :class:`Application` for serving static files during development.

It also provides several utilities for handling external media.
'''
import os
import re
import stat
import mimetypes
from email.utils import parsedate_tz, mktime_tz

from djpcms import views, Http404, http, html
from djpcms.utils.importer import import_module

# Third party application list.
third_party_applications = []

_media = None


w = html.Widget
wm = html.WidgetMaker
# Template for media index
static_index = wm().add(wm(tag='h1', key='title'),
                        html.List(key='nav'))


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


class StaticMapMixin(views.View):
    
    def title(self, request):
        return 'Index of ' + request.path
    
    @property
    def media_mapping(self):
        '''Load application media.'''
        global _media
        if _media is None:
            _media = application_map(self.settings.INSTALLED_APPS)
        return _media
    

class StaticRootView(StaticMapMixin):
    '''The root view for static files'''    
    def render(self, request):
        if self.appmodel.show_indexes:
            nav = (w('a', m, href=m+'/') for m in sorted(self.media_mapping))
            return static_index().render(request,
                            {'title': self.title(request),
                             'nav': nav})
            #html = self.template.render(request.template_file,
            #                    {'names':sorted(self.media_mapping),
            #                     'files':[],
            #                     'directory':directory,
            #                     'notroot':notroot})
        else:
            raise Http404()


class StaticFileView(StaticMapMixin):
    DEFAULT_CONTENT_TYPE = 'application/octet-stream'
    
    def __call__(self, request):
        mapping = self.media_mapping
        paths = request.urlargs['path'].split('/')
        app = paths.pop(0)
        if app in mapping:
            hd = mapping[app]
            fullpath = os.path.join(hd.absolute_path,*paths)
            if os.path.isdir(fullpath):
                if self.appmodel.show_indexes:
                    return self.directory_index(request, fullpath)
                else:
                    raise Http404()
            elif os.path.exists(fullpath):
                return self.serve_file(request, fullpath)
            else:
                raise Http404('No file "{0}" in application "{1}".\
 Could not render {1}'.format(paths,app))
        else:
            raise Http404()
        
    def directory_index(self, request, fullpath):
        names = [w('a', '../', href = '../', cn = 'folder')]
        files = []
        for f in sorted(os.listdir(fullpath)):
            if not f.startswith('.'):
                if os.path.isdir(os.path.join(fullpath, f)):
                    names.append(w('a', f, href = f+'/', cn = 'folder'))
                else:
                    files.append(w('a', f, href = f))
        names.extend(files)
        text = static_index().render(request,
                            {'title': self.title(request),
                             'nav': names})
        return http.Response(content = text.encode('latin-1','replace'),
                             content_type = 'text/html')
        
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
                                 content_type = mimetype,
                                 encoding = encoding)
        contents = open(fullpath, 'rb').read()
        response = http.Response(content = contents,
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
    default_route = '/favicon.ico'
    
    def __call__(self, request):
        if not request.urlargs:
            settings = self.settings
            mapping = self.media_mapping
            name = settings.FAVICON_MODULE or settings.SITE_MODULE
            if name in mapping:
                hd = mapping[name]
                fullpath = os.path.join(hd.absolute_path,'favicon.ico')
                return self.serve_file(request, fullpath)
        raise Http404()
    

class Static(views.Application):
    '''A simple application for handling static files.
    This application should be only used during development while
    leaving the task of serving media files to other servers in production.'''
    in_nav = 0
    has_plugins = False
    show_indexes = True
    root = StaticRootView()
    path = StaticFileView('<path:path>', parent_view = 'root')
    
    def __init__(self, *args, **kwargs):
        self.show_indexes = kwargs.pop('show_indexes',self.show_indexes)
        super(Static,self).__init__(*args,**kwargs)

