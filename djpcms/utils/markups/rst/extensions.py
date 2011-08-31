from djpcms import sites

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive


class StorageImage(Directive):
    """ Restructured text extension for inserting flickr images """
    
    has_content = True
    required_arguments = 2
    option_spec = {
    'image': directives.uri,
    }
    
    def image_url(self, url):
        return ''
    
    def run(self):
        storage = sites.storage
        image = ''
        if storage:
            url = storage.url(self.arguments[0])
            if url:
                image = self.image_html(url)
        return [nodes.raw('', image, format='html')]


def setup(app):
  app.add_directive('djp-image', StorageImage)