from py2py3 import UnicodeMixin

from djpcms.utils import force_str
from djpcms.template import mark_safe
from djpcms.core.page import block_htmlid
from djpcms.models import BlockContent
from djpcms.html import EMPTY_VALUE


class BlockContentGen(UnicodeMixin):
    '''Block Content Generator is responsible for generating contents within a ``block``.
A page is associated with a given url and a page has a certain number
of ``blocks`` depending on the template chosen for the pages: anything between 1 and 10 is highly possible.
Within each ``block`` there may be one or more ``contents``.

The edit mode block elements are rendered using the EDIT_BLOCK_TEMPLATES templates (see at top of file)
    '''
    def __init__(self, djp, b, editing):
        '''Initialize generator: *djp* is an instance of :class:`djpcms.views.response.DjpResponse`
and *b* is an integer indicating the ``block`` number in the page.'''
        self.djp     = djp
        self.page    = djp.page
        self.view    = djp.view
        self.request = djp.request
        self.editing = editing
        self.b       = b
        
    def render(self):
        '''Render the Block by looping over all the content block items
        '''
        edit = '' if not self.editing else 'sortable-block '
        id   = block_htmlid(self.page.id,self.b)
        def stream():
            yield '<div id="{0}" class="{1}djpcms-block">'.format(id,edit)
            for ht in self.blocks():
                if ht:
                    yield ht
            yield EMPTY_VALUE + '</div>'
        return force_str('\n'.join(stream()))
    
    def __unicode__(self):
        return self.render()
    
    def blocks(self):
        '''Function called within a template for generating all contents
        within a block.
        This function produce HTML only if self.view is based on a database Page
        object. Otherwise it does nothing.
        '''
        if self.editing:
            appmodel = self.djp.site.for_model(BlockContent)
            return appmodel.blocks(self.djp, self.page, self.b)
        else:
            blockcontents = BlockContent.objects.for_page_block(self.page, self.b)
            return self._blocks(blockcontents)
        
    def _blocks(self, blockcontents):
        '''
        Implementation of self.blocks when we are not in editing mode.
        Displaying the actual content of the block
        '''
        for b in blockcontents:
            yield b.render(self.djp)

