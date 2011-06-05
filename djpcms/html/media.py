'''Media Classes

Originally from django
'''
from itertools import chain

from py2py3 import urlparse

from djpcms.utils import mark_safe

urljoin = urlparse.urljoin

__all__ = ['MEDIA_TYPES', 'Media']


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

    @property
    def render_js(self):
        return (mark_safe('<script type="text/javascript" src="%s"></script>'\
                 % self.absolute_path(path)) for path in self._js)

    @property
    def render_css(self):
        # To keep rendering order consistent, we can't just iterate over items().
        # We need to sort the keys, and iterate over the sorted list.
        media = self._css.keys()
        media.sort()
        return chain(*[
            (mark_safe('<link href="%s" type="text/css" media="%s" rel="stylesheet" />' % (self.absolute_path(path), medium))
                    for path in self._css[medium])
                for medium in media])

    def absolute_path(self, path, prefix=None):
        if path.startswith('http://') or path.startswith('https://') or path.startswith('/'):
            return path
        if prefix is None:
            from djpcms import sites
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
        if isinstance(other,Media):
            combined = Media()
            for name in MEDIA_TYPES:
                getattr(combined, 'add_' + name)(getattr(self, '_' + name, None))
                getattr(combined, 'add_' + name)(getattr(other, '_' + name, None))
            return combined
        else:
            return self

