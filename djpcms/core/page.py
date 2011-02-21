import sys
import re
import logging

import djpcms
from djpcms import sites
from djpcms.utils import force_str
from djpcms.template import loader, escape
from djpcms.core.exceptions import BlockOutOfBound
from djpcms.plugins import get_wrapper, default_content_wrapper, get_plugin
import djpcms.contrib.flowrepo.markups as markuplib


contentre = re.compile('{{ content\d }}')


def block_htmlid(pageid, block):
    '''HTML id for a block container. Used throughout the library.'''
    return 'djpcms-block-{0}-{1}'.format(pageid,block)


class PageInterface(object):
    '''Page object interface'''
    
    def numblocks(self):
        raise NotImplementedError
    
    def create_template(self, name, templ):
        raise NotImplementedError
    
    def set_template(self, template):
        self.inner_template = template
        self.save()
        
    def get_template(self, djp = None):
        '''Returns the name of the ``HTML`` template file for the page.
If not specified we get the template of the :attr:`parent` page.'''
        if not self.template:
            if self.parent:
                return self.parent.get_template(djp)
            else:
                sett = sites.settings if not djp else djp.settings
                return sett.DEFAULT_TEMPLATE_NAME
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
    
    
class TemplateInterface(object):
    
    def render(self, c):
        '''Render the inner template given the context ``c``.
        '''
        return loader.template_class(self.template).render(c)
    
    def numblocks(self):
        '''Number of ``blocks`` within template.'''
        bs = self.blocks.split(',')
        return len(bs)
    
    def blocks_from_content(self):
        cs = contentre.findall(self.template)
        self.blocks = ','.join((c[3:-3] for c in cs))
    

class BlockInterface(object):
    '''Content Block Interface'''
    logger  = logging.getLogger('BlockContent')
    
    def render(self, djp, plugin = None, wrapper = None):
        '''Render the plugin in the content block
This function call the plugin render function and wrap the resulting HTML
with the wrapper callable.'''
        html = ''
        try:
            site = djp.site
            plugin  = plugin or self.plugin
            wrapper = wrapper or self.wrapper
            if plugin:
                if site.permissions.has(djp.request,djpcms.VIEW, self):
                    djp.media += plugin.media
                    html = plugin(djp, self.arguments, wrapper = wrapper)
        except Exception as e:
            if getattr(djp.settings,'TESTING',False):
                raise
            exc_info = sys.exc_info()
            self.logger.error('%s - block %s -- %s' % (plugin,self,e),
                exc_info=exc_info,
                extra={'request':djp.request}
            )
            if djp.request.user.is_superuser:
                html = escape('%s' % e)
        
        if html:
            return wrapper(djp, self, html)
        else:
            return html
        
    def htmlid(self):
        return 'blockcontent-{0}'.format(self)
    
    def pluginid(self, extra = ''):
        p = 'plugin-{0}'.format(self)
        if extra:
            p = '{0}-{1}'.format(p,extra)
        return p
            
    def htmlid(self):
        return 'block-%s-%s-%s' % (self.page.id,self.block,self.position)
    
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
        '''Get contentblocks for a given page and block
        @param page: instance of a page model
        @param block: integer indicating the block number
        @return: a queryset  
        '''
        blockcontents = self.filter(page = page, block = block)
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
    
    def htmlbody(self):
        text = self.body
        if not text:
            return ''
        mkp = markuplib.get(self.markup)
        if mkp:
            handler = mkp.get('handler')
            text = handler(text)
            text = loader.mark_safe(force_str(text))
        return text
    
    