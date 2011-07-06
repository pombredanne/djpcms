'''Media Classes

Originally from django
'''
from itertools import chain
from copy import deepcopy

from py2py3 import urlparse

from djpcms import sites
from djpcms.utils import mark_safe

urljoin = urlparse.urljoin

__all__ = ['MEDIA_TYPES', 'Media']


MEDIA_TYPES = ('css','js')

class Media(object):
    '''Originally from django, it is used for manipulating media files such as style sheet and javascript.
It is used by :class:`djpcms.views.RendererMixin` classes to include extra media into the page they are rendering.
A typical example::

    >>> from djpcms.html import Media
    >>> m = Media(js = ['one/jsfile/blabla.js','onother/one/pluto.js'],
                  css = {'all':['css/style.css','css/theme.css']})
              
There are two properties used for rendering, they both return a generator over media files::
    
    >>> list(m.render_js)
    ['<script type="text/javascript" src="one/jsfile/blabla.js"></script>',
     '<script type="text/javascript" src="onother/one/pluto.js"></script>']
    
    >>> list(m.render_css)
    ['<link href="css/style.css" type="text/css" media="all" rel="stylesheet" />',
     '<link href="css/theme.css" type="text/css" media="all" rel="stylesheet" />']

'''
    __slots__ = ('_css','_js')
    
    def __init__(self, media=None, **kwargs):
        if media:
            media_attrs = {'_css':media._css,'_js':media_js}
        else:
            media_attrs = kwargs

        self._css = {}
        self._js = []

        for name in MEDIA_TYPES:
            getattr(self, 'add_' + name)(media_attrs.get(name, None))

    @property
    def render_js(self):
        '''Generator over javascript scripts to be included in the page.'''
        return (mark_safe('<script type="text/javascript" src="%s"></script>'\
                 % self.absolute_path(path)) for path in self._js)

    @property
    def render_css(self):
        '''Generator over css stylesheets to be included in the page.'''
        media = self._css.keys()
        media.sort()
        return chain(*[
            (mark_safe('<link href="%s" type="text/css" media="%s" rel="stylesheet" />' % (self.absolute_path(path), medium))
                    for path in self._css[medium])
                for medium in media])

    def absolute_path(self, path, prefix=None):
        if path.startswith('http://') or path.startswith('https://') or path.startswith('/'):
            return path
        prefix = sites.settings.MEDIA_URL if prefix is None and sites.settings else ''
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
                    if not self._css.get(medium) or path not in self._css[medium]:
                        self._css.setdefault(medium, []).append(path)

    def add(self, other):
        if isinstance(other,Media):
            for name in MEDIA_TYPES:
                getattr(self, 'add_{0}'.format(name))(\
                            getattr(other, '_{0}'.format(name)))
        return self

    #def __add__(self, other):
    #    if isinstance(other,Media):
    #        combined = Media()
    #        for name in MEDIA_TYPES:
    #            getattr(combined, 'add_' + name)(getattr(self, '_' + name, None))
    #            getattr(combined, 'add_' + name)(getattr(other, '_' + name, None))
    #        return combined
    #    else:
    #        return self
