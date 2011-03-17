'''Media Classes

Originally from django
'''
from itertools import chain

from py2py3 import urlparse

from djpcms import sites
from djpcms.template import loader

mark_safe = loader.mark_safe
urljoin = urlparse.urljoin

__all__ = ['MEDIA_TYPES',
           'Media',
           'media_property',
           'MediaDefiningClass',
           'BaseMedia']


MEDIA_TYPES = ('css','js')

class Media(object):

    def __init__(self, media=None, **kwargs):
        if media:
            media_attrs = media.__dict__
        else:
            media_attrs = kwargs

        self._css = {}
        self._js = []

        for name in MEDIA_TYPES:
            getattr(self, 'add_' + name)(media_attrs.get(name, None))

    def html(self):
        return loader.mark_safe(self.render())
                                
    def render(self):
        return '\n'.join(chain(*[getattr(self, 'render_' + name)() for name in MEDIA_TYPES]))

    @property
    def render_js(self):
        return ('<script type="text/javascript" src="%s"></script>' % self.absolute_path(path) for path in self._js)

    @property
    def render_css(self):
        # To keep rendering order consistent, we can't just iterate over items().
        # We need to sort the keys, and iterate over the sorted list.
        media = self._css.keys()
        media.sort()
        return chain(*[
            ('<link href="%s" type="text/css" media="%s" rel="stylesheet" />' % (self.absolute_path(path), medium)
                    for path in self._css[medium])
                for medium in media])

    def absolute_path(self, path, prefix=None):
        if path.startswith('http://') or path.startswith('https://') or path.startswith('/'):
            return path
        if prefix is None:
            prefix = sites.settings.MEDIA_URL
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

    def __add__(self, other):
        combined = Media()
        for name in MEDIA_TYPES:
            getattr(combined, 'add_' + name)(getattr(self, '_' + name, None))
            getattr(combined, 'add_' + name)(getattr(other, '_' + name, None))
        return combined


def media_property(cls):
    def _media(self):
        # Get the media property of the superclass, if it exists
        if hasattr(super(cls, self), 'media'):
            base = super(cls, self).media
        else:
            base = Media()

        # Get the media definition for this class
        definition = getattr(cls, 'Media', None)
        if definition:
            extend = getattr(definition, 'extend', True)
            if extend:
                if extend == True:
                    m = base
                else:
                    m = Media()
                    for medium in extend:
                        m = m + base[medium]
                return m + Media(definition)
            else:
                return Media(definition)
        else:
            return base
    return property(_media)


class MediaDefiningClass(type):
    "Metaclass for classes that can have media definitions"
    def __new__(cls, name, bases, attrs):
        super_new = super(MediaDefiningClass, cls).__new__
        parents = [b for b in bases if isinstance(b, MediaDefiningClass)]
        if not parents or attrs.pop('virtual',False):
            return super_new(cls, name, bases, attrs)
        new_class = super_new(cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        return new_class
    

BaseMedia = MediaDefiningClass('BaseMedia',(object,),{})
