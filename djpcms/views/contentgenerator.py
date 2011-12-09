from djpcms.utils import force_str
from djpcms.core.page import block_htmlid
from djpcms.html import EMPTY_VALUE, Widget, blockelement, ContextRenderer


__all__ = ['BlockContentGen','InnerContent']



class BlockContentGen(ContextRenderer):
    '''Block Content Generator is responsible for generating contents
within a ``block``. A page is associated with a given url and a
page has a certain number of ``blocks`` depending on the template
chosen for the pages: anything between 1 and 10 is highly possible.
Within each ``block`` there may be one or more ``contents``.

The edit mode block elements are rendered using the EDIT_BLOCK_TEMPLATES
templates (see at top of file)
    '''
    def __init__(self, request, b, editing = False):
        super(BlockContentGen,self).__init__(request)
        self.page = request.page
        self.editing = editing
        self.b = b
        self.context.update(((n,ht) for n,ht in enumerate(self.blocks()) if ht))
        
    def stream(self):
        edit = '' if not self.editing else 'sortable-block '
        if self.page:
            id   = block_htmlid(self.page.id,self.b)
            yield '<div id="{1}" class="{0}djpcms-block">'.format(edit,id)
        else:
            yield '<div class="{0}djpcms-block">'.format(edit)
        ctx = self.context
        for k in sorted(self.context):
            yield ctx[k]
        yield '{0}</div>'.format(EMPTY_VALUE)
            
    def render(self):
        return '\n'.join(self.stream())
    
    def blocks(self):
        '''Function called within a template for generating all contents
        within a block.
        This function produce HTML only if self.view is based on a database Page
        object. Otherwise it does nothing.
        '''
        BlockContent = self.request.view.BlockContent
        if self.editing:
            appmodel = self.request.view.site.for_model(BlockContent)
            return appmodel.blocks(self.request, self.page, self.b)
        else:
            b = BlockContent.model.for_page_block(BlockContent,\
                                                   self.page, self.b)\
                 if self.page else (blockelement(b) for b in self.b)
            return self._blocks(b)
        
    def _blocks(self, blockcontents):
        '''
        Implementation of self.blocks when we are not in editing mode.
        Displaying the actual content of the block
        '''
        for b in blockcontents:
            yield b.render(self.request)

    
class InnerContent(ContextRenderer):

    def __init__(self, request, inner_template, editing):
        super(InnerContent,self).__init__(request)
        self.inner_template = inner_template
        self.numblocks = inner_template.numblocks()
        self.editing = editing
        self.context.update((('content%s' % b,
                              BlockContentGen(request, b, editing))\
                                for b in range(self.numblocks)))
    
    def render(self):
        view = self.request.view
        loader = view.template
        return self.inner_template.render(
                    view.template,
                    view.site.context(self.context, request=self.request))

