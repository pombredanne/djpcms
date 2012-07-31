'''\
:class:`Page` and :class:`Block` are used by djpcms to allow for
page customization on a running web page rather than during design.
The use of this features requires a backend database model to be implemented.
'''
import sys
import re
import logging

from djpcms.html import NON_BREACKING_SPACE, htmldoc
from djpcms.html.layout import grid
from djpcms.utils import markups
from djpcms.utils.text import escape, to_string, NOTHING

from .exceptions import BlockOutOfBound
from .routing import Route
from . import permissions
from .plugins import get_wrapper, default_content_wrapper, get_plugin


__all__ = ['PageModel',
           'BlockModel',
           'MarkupMixin']


def block_htmlid(pageid, block):
    '''HTML id for a block container. Used throughout the library.'''
    return 'djpcms-block-{0}-{1}'.format(pageid,block)


class PageModel(object):
    '''Page object interface.

.. attribute:: route

    The :class:`djpcms.Route` for this page

The following attributes must be implemented by subclasses.

.. attribute:: url

    The web site relative url

.. attribute:: layout
'''
    layout = 0
    layout = None
    inner_template = None
    grid_system = None

    @property
    def route(self):
        return Route(self.url)

    @property
    def inner_grid(self):
        try:
            return grid(self.inner_template)
        except:
            return None

    @property
    def path(self):
        return self.url

    def numblocks(self):
        grid = self.inner_grid
        if grid:
            return grid.numblocks
        else:
            return 1

    def add_plugin(self, p, block = 0):
        '''Add a plugin to a block'''
        b = self.get_block(block)
        try:
            name = p.name
        except:
            name = p
        b.plugin_name = name
        b.save()
        return b

    def get_block(self, block, position = None):
        nb = self.numblocks()
        if block < 0 or block >= nb:
            raise BlockOutOfBound('Page has {0} blocks'.format(nb))
        return self._get_block(block, position)

    # INTERNALS

    def _get_block(self, block, position):
        raise NotImplementedError

    def get_level(self):
        try:
            url = self.url
            if url.startswith('/'):
                url = url[1:]
            if url.endswith('/'):
                url = url[:-1]
            if url:
                bits  = url.split('/')
                level = len(bits)
            else:
                level = 0
        except:
            level = 1
        return level

    def doc_type(self):
        d = self.doctype
        return htmldoc(d)

    @classmethod
    def register_tree_update(cls, tree_update):
        pass

    @classmethod
    def blocks(cls, pageobj):
        '''Iterator over block contents'''
        raise NotImplementedError()

    @classmethod
    def make_block(cls, **kwargs):
        raise NotImplementedError()


class BlockModel(object):
    '''Content Block Interface.'''
    logger  = logging.getLogger('BlockContent')
    namespace = 'content'
    row = 1

    def widget(self, request, plugin=None, wrapper=None):
        '''Render the plugin in the content block
This function call the plugin render function and wrap the resulting HTML
with the wrapper callable.'''
        plugin_response = None
        plugin = plugin or self.plugin
        wrapper = wrapper or self.wrapper
        if plugin and request.has_permission(permissions.VIEW, self):
            try:
                request.media.add(plugin.media(request))
                plugin_response = plugin(request, self.arguments, block=self)
            except Exception as e:
                exc_info = sys.exc_info()
                request.cache.traces.append(exc_info)
                self.logger.error('%s - block %s -- %s' % (plugin,self,e),
                    exc_info=exc_info,
                    extra={'request':request}
                )
                if request.user.is_superuser:
                    plugin_response = escape('%s' % e)

        # html can be a string or whatever the plugin returns.
        if plugin_response not in NOTHING or not self.position:
            if plugin_response in NOTHING:
                plugin_response = NON_BREACKING_SPACE
            return wrapper(request, self, plugin_response)

    def pluginid(self, extra = ''):
        p = 'plugin-{0}'.format(self)
        if extra:
            p = '{0}-{1}'.format(p,extra)
        return p

    def htmlid(self, edit=False):
        return 'edit-block-%s' % self.id if edit else 'block-%s' % self.id

    def __unicode__(self):
        return self.htmlid()

    @classmethod
    def block_from_html_id(cls, htmlid):
        id = htmlid.split('-')
        if len(id) > 1:
            id = id[-1]
            return cls.objects.get(id=id)
        else:
            return None

    def __get_plugin(self):
        return get_plugin(self.plugin_name)
    plugin = property(__get_plugin)

    def _get_wrapper(self):
        return get_wrapper(self.container_type, default_content_wrapper)
    wrapper = property(_get_wrapper)

    def plugin_class(self):
        '''Return the class of the embedded plugin (if available)
        otherwise it returns Null
        '''
        if self.plugin:
            return self.plugin.__class__
        else:
            return None

    @classmethod
    def for_page_block(cls, mapper, page, block):
        '''\
Get contentblocks for a given page and block

:parameter page: instance of a :class:`PageInterface` model
:parameter block: integer indicating the block number.

Return an iterable over ordered items (by position) in block
'''
        blockcontents = sorted(mapper.filter(page = page, block = block),
                               key = lambda x : x.position)
        create = False
        pos = None

        # No contents, create an empty one
        if not blockcontents:
            create = True
            pos    = 0
        # Last content has a plugin. Add another block
        elif blockcontents[-1].plugin_name:
            create = True
            pos = blockcontents[-1].position + 1

        if create:
            bc = mapper.model(page = page, block = block, position = pos)
            bc.save()
            return mapper.filter(page = page, block = block)
        else:
            return blockcontents


class MarkupMixin(object):

    def tohtml(self, text):
        if not text:
            return ''
        mkp = markups.get(self.markup)
        if mkp:
            handler = mkp.get('handler')
            text = handler(text)
            text = loader.mark_safe(to_string(text))
        return text

