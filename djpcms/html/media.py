'''Media Class

Originally from django
'''
from itertools import chain
from copy import deepcopy

from py2py3 import urlparse

from djpcms.utils import mark_safe

urljoin = urlparse.urljoin

__all__ = ['MEDIA_TYPES', 'Media']


MEDIA_TYPES = ('css','js')

class Media(object):
    '''Originally from django, it is used for manipulating media
files such as style sheet and javascript.
'''
    __slots__ = ('_css','_js','settings')
    
    def __init__(self, media=None, settings = None, **kwargs):
        if media:
            media_attrs = {'_css':media._css,'_js':media_js}
        else:
            media_attrs = kwargs

        self.settings = settings
        self._css = {}
        self._js = []

        for name in MEDIA_TYPES:
            getattr(self, 'add_' + name)(media_attrs.get(name, None))

    def render_js(self):
        '''Generator over javascript scripts to be included in the page.'''
        settings = self.settings or {}
        prefix = settings.get('MEDIA_URL','')
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
        '''Generator over css stylesheets to be included in the page.'''
        settings = self.settings or {}
        prefix = settings.get('MEDIA_URL','')
        absolute = self.absolute_path
        media = self._css.keys()
        media.sort()
        return chain(*[
            (mark_safe('<link href="%s" type="text/css" media="%s"\
 rel="stylesheet" />' % (absolute(path,prefix), medium))
                    for path in self._css[medium])
                for medium in media])

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
            for medium, paths in data.items():
                for path in paths:
                    if not self._css.get(medium) or path not in\
                         self._css[medium]:
                        self._css.setdefault(medium, []).append(path)

    def add(self, other):
        if isinstance(other,Media):
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
