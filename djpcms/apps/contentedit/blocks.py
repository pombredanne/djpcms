from djpcms import forms, html, views, ajax
from djpcms.core.page import block_htmlid
from djpcms.core.exceptions import PermissionDenied
from djpcms.plugins.extrawrappers import CollapsedWrapper
from djpcms.utils import mark_safe

from .layout import ContentBlockHtmlForm, PLUGIN_DATA_FORM_CLASS,\
                    BlockLayoutFormHtml


__all__ = ['ContentApplication']


edit_class = 'edit-block ui-state-active'
movable_class = 'movable'
edit_movable = edit_class + ' ' + movable_class


# Content wrapper in editing mode.
# Only called by content_view (function above)
class EditWrapperHandler(CollapsedWrapper):
    '''a :class:`djpcms.plugins.DJPwrapper` for
editing content.'''
    auto_register = False
    header_classes = CollapsedWrapper.header_classes + ' ui-state-active'
    body_classes = CollapsedWrapper.body_classes + ' plugin-form'
    
    def __init__(self, url):
        self.url = url
        
    def __call__(self, request, cblock, html):
        return self.wrap(request, cblock, html)
    
    def title(self, cblock):
        if cblock.plugin:
            return cblock.plugin.description
        else:
            return 'Content Editor'
    
    def id(self, cblock):
        return 'edit-{0}'.format(cblock.htmlid())
    
    def _wrap(self, request, cblock, html):
        if cblock.plugin_name:
            cl = edit_movable
        else:
            cl = edit_class
        return cl,request.viewurl('delete', instance = request.instance)
    
    def footer(self, request, cblock, html):
        return request.view.get_preview(request, request.instance, self.url)


class BlockChangeView(views.ChangeView):
    
    def block_from_edit_id(self, id):
        id = '-'.join(id.split('-')[1:])
        return self.model.block_from_html_id(id)             


class ChangeLayoutView(BlockChangeView):
    pass


class ChangeContentView(BlockChangeView):
    '''View class for managing inline editing of a content block.
    '''    
    def get_preview(self, request, instance, url, plugin = None):
        '''Render a plugin and its wrapper for preview within a div element'''
        request = request.for_url(url)
        if not request:
            return 'Could not get preview'
        
        try:
            preview_html = instance.render(request, plugin = plugin)
        except Exception as e:
            preview_html = str(e)
        
        cb = lambda phtml : mark_safe('<div id="%s" class="preview">%s</div>' %\
                                      (instance.pluginid('preview'),phtml))
        if preview_html:
            return request.view.response(preview_html, callback = cb)
        else:
            return ''
        
    def get_plugin_form(self, request, plugin, prefix):
        '''Retrieve the plugin editing form if ``plugin`` is not ``None``.'''
        if plugin:
            instance = request.instance
            args     = None
            if instance.plugin == plugin:
                args = instance.arguments
            return plugin.get_form(request, args, prefix = prefix)
            
    def edit_block(self, request):
        return jhtmls(identifier = '#' + self.instance.pluginid(),
                      html = self.instance.plugin_edit_block(request))
    
    def ajax__container_type(self, request):
        return self.handle_content_block_changes(request, commit = False)
    
    def ajax__plugin_name(self, request):
        return self.handle_content_block_changes(request, commit = False)
    
    def port_response(self, request):
        return self.handle_content_block_changes(djp)
        
    def ajax__edit_content(self, djp):
        pluginview = self.appmodel.getview('plugin')
        return pluginview.port_response(pluginview(djp.request,
                                                  instance = djp.instance))
    
    def render(self, djp, url = None):
        formhtml = self.get_form(djp,
                                 initial = {'url': url},
                                 force_prefix = True)
        instance = djp.instance
        plugin = instance.plugin
        if not plugin:
            return ''
        form = formhtml.form
        prefix = form.prefix
        pform = self.get_plugin_form(djp, instance.plugin, prefix)
        html = '' if not pform else pform.render(djp)
        edit_url = plugin.edit_url(djp,instance.arguments)
        if edit_url:
            edit_url = HtmlWrap('a',
                                cn = 'ajax button',
                                inner='Edit')\
                             .addAttr('href',edit_url)\
                             .addAttr('title','Edit plugin')\
                             .addData('method','get')
            formhtml.inputs.append(edit_url)
        return formhtml.render(djp, plugin = html)
    
    def handle_content_block_changes(self, djp, commit = True):
        '''View called when changing the content plugin values.
The instance.plugin object is maintained but its fields may change.'''
        instance = djp.instance
        request = djp.request
        fhtml = self.get_form(djp, withdata = True, force_prefix = True)
        form = fhtml.form
        prefix = form.prefix
        layout = fhtml.layout
        if not form.is_valid():
            return layout.json_messages(form)        
        data = form.cleaned_data
        url = data['url']
        pform = self.get_plugin_form(djp, data['plugin_name'], prefix)
        
        if commit and pform and not pform.is_valid():
            return layout.json_messages(pform.form)
        
        if pform is not None:
            instance.arguments = instance.plugin.save(pform.form)
            pform.tag = None
            plugin_options = pform.render(djp)
        else:
            plugin_options = '' if not pform else pform.render(djp)
        instance = form.save(commit = commit)
        jquery = ajax.jhtmls(identifier = '.' + PLUGIN_DATA_FORM_CLASS,
                             html = plugin_options,
                             alldocument = False)
        preview = self.get_preview(djp, instance, url)
        jquery.add('#%s' % instance.pluginid('preview'), preview)
        
        if commit:
            form.add_message("Plugin changed to %s"\
                              % instance.plugin.description)
            
        jquery.update(layout.json_messages(form))
        return jquery

    def ajax__rearrange(self, djp):
        '''Move the content block to a new position.'''
        request = djp.request
        contentblock = djp.instance
        data   = request.REQUEST
        try:            
            previous = data.get('previous',None)
            if previous:
                block = self.block_from_edit_id(previous)
                pos = block.position
                newposition = pos + 1
            else:
                nextv = data.get('next',None)
                if nextv:
                    block = self.block_from_edit_id(nextv)
                    pos = block.position
                else:
                    return jempty()
                newposition = pos if not pos else pos-1
            
            block = block.block
            if block != contentblock.block or\
               contentblock.position != newposition:
                # modify positions in the drop box
                for bc in self.model.objects.filter(page = contentblock.page,
                                                    block = block):
                    if bc.position < newposition:
                        continue
                    bc.position += 1
                    bc.save()
                contentblock.position = newposition
                contentblock.block = block
                contentblock.save()
                #update_page(self.model,page)
            return ajax.jempty()
        except Exception as e:
            return ajax.jerror('Could not find target block. {0}'.format(e))
        
        
class DeleteContentView(views.DeleteView):
    
    def port_response(self, request):
        instance = request.instance
        block  = instance.block
        jquery = ajax.jcollection()
        blockcontents = self.model.objects.for_page_block(instance.page, block)
        if instance.position == len(blockcontents) - 1:
            return jquery
        
        jatt   = ajax.jattribute()
        pos    = 0
        for b in blockcontents:
            if b == instance:
                jquery.append(ajax.jremove('#'+instance.htmlid()))
                b.delete()
                continue
            if b.position != pos:
                b.position = pos
                b.save()
            pos += 1
        jquery.append(jatt)

        if request.is_xhr:
            return jquery
        else:
            refer = sjp.request.environ.get('HTTP_REFERER')
            return self.redirect(refer)


class ContentApplication(views.Application):
    '''AJAX enabled :class:`djpcms.views.Application` for changing
content in a content block.'''
    form = ContentBlockHtmlForm
    has_plugins = False
    url_bits_mapping = {'contentblock':'id'}
    
    search = views.SearchView()
    view = views.ViewView('<int:contentblock>/')
    change = ChangeContentView()
    layout = ChangeLayoutView('layout/', form = BlockLayoutFormHtml)
    delete = DeleteContentView()
    
    def on_bound(self):
        self.root.internals['BlockContent'] = self.mapper
    
    def submit(self, *args, **kwargs):
        return [html.Widget('input:submit', value = "save", name = '_save')]
    
    def remove_object(self, obj):
        bid = obj.htmlid()
        if self.model.objects.delete_and_sort(obj):
            return bid

    def blockhtml(self, request, instance, editview, wrapper):
        '''A content block rendered in editing mode'''
        request = request.for_view_args(editview, instance = instance)
        html = request.render(url = request.url)
        #layoutview = self.getview('layout')
        #html0 =  layoutview(djp.request, instance = instance).render()
        # html = html0 + html
        return wrapper(request,instance,html)
            
    def blocks(self, request, page, blocknum):
        '''Return a generator of edit blocks.
        '''
        blockcontents = self.model.objects.for_page_block(page, blocknum)
        url      = request.url
        editview = self.views.get('change')
        wrapper  = EditWrapperHandler(url)
        Tot = len(blockcontents) - 1
        # Clean blocks
        pos = 0
        t = 0
        last = None
        for b in blockcontents:
            last = b
            if not b.plugin_name and t < Tot:
                b.delete()
                last = None
                continue
            else:
                if b.position != pos:
                    b.position = pos
                    b.save()
                if b.plugin_name:
                    last = None
                pos += 1
            yield self.blockhtml(request, b, editview, wrapper)
            
        # Create last block
        if last == None:
            last = self.model(page = page, block = blocknum, position = pos)
            last.save()
            yield self.blockhtml(request, last, editview, wrapper)
