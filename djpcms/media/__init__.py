'''Sylesheet generator and Javascript assets aggregator for djpcms.'''
import os
from copy import deepcopy

from djpcms.utils.text import mark_safe
from djpcms.utils.httpurl import urljoin

from .js import *

MEDIA_TYPES = ('css','js')


def site_media_file(settings, name=None, directory=False):
    if name is None:
        name = '%s.css' % settings.STYLING
    if directory:
        mdir = os.path.join(settings.SITE_DIRECTORY, 'media', settings.SITE_MODULE)
        if os.path.isdir(mdir):
            return os.path.join(mdir, name)
    else:
        return '%s/%s' % (settings.SITE_MODULE, name)
    
    
class Media(object):
    '''Originally from django, it is used for manipulating media
files such as style sheet and javascript.'''
    __slots__ = ('_css','_js','_settings')
    
    def __init__(self, media=None, settings=None, **kwargs):
        if media:
            media_attrs = {'_css':media._css,'_js':media_js}
        else:
            media_attrs = kwargs

        self._settings = settings or {}
        self._css = {}
        self._js = []

        for name in MEDIA_TYPES:
            getattr(self, 'add_' + name)(media_attrs.get(name, None))

    @property
    def settings(self):
        return self._settings
    
    def render_js(self):
        '''Generator over javascript scripts to be included in the page.'''
        prefix = self.settings.get('MEDIA_URL','')
        absolute = self.absolute_path
        for path in self._js:
            path = absolute(path,prefix)
            yield mark_safe('<script type="text/javascript"\
 src="{0}"></script>'.format(path))
    
    @property
    def all_js(self):
        return '\n'.join(self.render_js())
    
    @property
    def render_css(self):
        prefix = self.settings.get('MEDIA_URL','')
        absolute = self.absolute_path
        done = set()
        for medium in sorted(self._css):
            paths = self._css[medium]
            medium = '' if medium == 'all' else " media='%s'" % medium
            for path in paths:
                url = path[0]
                if url in done:
                    continue
                done.add(url)
                link = "<link href='%s' type='text/css'%s rel='stylesheet'/>"\
                        % (absolute(url, prefix), medium)
                if len(path) == 2:
                    link = '<!--[if %s]>%s<![endif]-->' % (path[1],link)
                yield mark_safe(link)
        
    def absolute_path(self, path, prefix=None):
        if path.startswith('http://') or path.startswith('https://')\
         or path.startswith('/'):
            return path
        return urljoin(prefix, path)

    def __getitem__(self, name):
        "Returns a Media object that only contains media of the given type"
        if name in MEDIA_TYPES:
            return Media(**{str(name): getattr(self, '_' + name)})
        raise KeyError('Unknown media type "%s"' % name)

    def add_js(self, data):
        if data:
            for path in data:
                if path not in self._js:
                    self._js.append(path)

    def add_css(self, data):
        if data:
            css = self._css
            for medium, paths in data.items():
                if medium not in css:
                    css[medium] = []
                medium = css[medium]
                for path in paths:
                    if not isinstance(path,(tuple,list)):
                        path = (path,)
                    medium.append(path)

    def add(self, other):
        if isinstance(other, Media):
            for name in MEDIA_TYPES:
                getattr(self, 'add_{0}'.format(name))(\
                            getattr(other, '_{0}'.format(name)))
        return self

    def __add__(self, other):
        if isinstance(other,Media):
            js = deepcopy(self._js)
            css = deepcopy(self._css)
            combined = Media(js = js, css = css)
            return combined.add(other)
        else:
            return self
