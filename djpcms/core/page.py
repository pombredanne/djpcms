import sys
import re
import logging

import djpcms
from djpcms.core.exceptions import BlockOutOfBound
from djpcms.plugins import get_wrapper, default_content_wrapper, get_plugin
from djpcms.utils import markups, escape, force_str
from djpcms.html import htmldoc


contentre = re.compile('{{ content\d }}')


def block_htmlid(pageid, block):
    '''HTML id for a block container. Used throughout the library.'''
    return 'djpcms-block-{0}-{1}'.format(pageid,block)


class Page(object):
    '''Page object interface'''
    
    def numblocks(self):
        raise NotImplementedError
    
    def blocks(self):
        '''Iterator over block contents'''
        raise NotImplementedError
    
    def create_template(self, name, templ):
        raise NotImplementedError
    
    def set_template(self, template):
        self.inner_template = template
        self.save()
        
    def get_template(self, djp):
        '''Returns the name of the ``HTML`` template file for the page.'''
        if not self.template:
            return djp.site.settings.DEFAULT_TEMPLATE_NAME
        else:
            return self.template
    
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
    
    
class Template(object):
    
    def render(self, loader, c):
        '''Render the inner template given the context ``c``.
        '''
        return loader.render_from_string(self.template,c)
    
    def numblocks(self):
        '''Number of ``blocks`` within template.'''
        bs = self.blocks.split(',')
        return len(bs)
    
    def blocks_from_content(self):
        cs = contentre.findall(self.template)
        self.blocks = ','.join((c[3:-3] for c in cs))
    

class Block(object):
    '''Content Block Interface'''
    logger  = logging.getLogger('BlockContent')
    
    def render(self, djp, plugin = None, wrapper = None):
        '''Render the plugin in the content block
This function call the plugin render function and wrap the resulting HTML
with the wrapper callable.'''
        plugin_response = None
        site = djp.site
        plugin = plugin or self.plugin
        wrapper = wrapper or self.wrapper
        if plugin and site.permissions.has(djp.request,djpcms.VIEW, self):
            try:
                djp.media.add(plugin.media())
                plugin_response = plugin(djp, self.arguments, block = self)
            except Exception as e:
                if getattr(djp.settings,'TESTING',False):
                    raise
                self.logger.error('%s - block %s -- %s' % (plugin,self,e),
                    exc_info=True,
                    extra={'request':djp.request}
                )
                if djp.request.user.is_superuser:
                    plugin_response = escape('%s' % e)
        
        # html can be a string or whatever the plugin returns.
        if plugin_response is not None:
            callback = lambda r : wrapper(djp, self, r)
            return djp.root.render_response(plugin_response, callback)
    
    def pluginid(self, extra = ''):
        p = 'plugin-{0}'.format(self)
        if extra:
            p = '{0}-{1}'.format(p,extra)
        return p
            
    def htmlid(self):
        return 'block-{0}'.format(self.id)
    
    def __unicode__(self):
        return self.htmlid()
    
    @classmethod
    def block_from_html_id(cls, htmlid):
        id = htmlid.split('-')
        if len(id) == 2:
            id = id[1]
            return cls.objects.get(id = id)
        else:
            return None
        
    def __get_plugin(self):
        return get_plugin(self.plugin_name)
    plugin = property(__get_plugin)
        
    def _get_wrapper(self):
        return get_wrapper(self.container_type,default_content_wrapper)
    wrapper = property(_get_wrapper)
    
    def plugin_class(self):
        '''Return the class of the embedded plugin (if available)
        otherwise it returns Null
        '''
        if self.plugin:
            return self.plugin.__class__
        else:
            return None
    
    
    
class BlockContentManager(object):
    
    def for_page_block(self, page, block):
        '''\
Get contentblocks for a given page and block

:parameter page: instance of a :class:`PageInterface` model
:parameter block: integer indicating the block number.

Return an iterable over ordered items (by position) in block  
'''
        blockcontents = sorted(self.filter(page = page, block = block),
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
            bc = self.model(page = page, block = block, position = pos)
            bc.save()
            return self.filter(page = page, block = block)
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
            text = loader.mark_safe(force_str(text))
        return text
    
    
