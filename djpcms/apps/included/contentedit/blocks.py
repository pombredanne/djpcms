from djpcms import forms
from djpcms.forms import FormType, HtmlForm, SubmitInput, HtmlWidget
from djpcms.core.page import block_htmlid
from djpcms.utils.translation import gettext as _
from djpcms.core.exceptions import PermissionDenied
from djpcms.template import loader
from djpcms.utils.ajax import jhtmls, jremove, dialog, jempty
from djpcms.utils.ajax import jerror, jattribute, jcollection
from djpcms.plugins.extrawrappers import CollapsedWrapper
from djpcms.utils import mark_safe
from djpcms import views

from .layout import ContentBlockHtmlForm, PLUGIN_DATA_FORM_CLASS


edit_class = 'edit-block ui-state-active'
movable_class = 'movable'
edit_movable = edit_class + ' ' + movable_class


# Content wrapper in editing mode.
# Only called by content_view (function above)
class EditWrapperHandler(CollapsedWrapper):
    '''Wrapper for editing content
    '''
    auto_register = False
    header_classes = CollapsedWrapper.header_classes + ' ui-state-active'
    
    def __init__(self, url):
        self.url = url
        
    def __call__(self, djp, cblock, html):
        return self.wrap(djp, cblock, html)
    
    def title(self, cblock):
        if cblock.plugin:
            return cblock.plugin.description
        else:
            return 'Content Editor'
    
    def id(self, cblock):
        return 'edit-{0}'.format(cblock.htmlid())
    
    def _wrap(self, djp, cblock, html):
        if cblock.plugin_name:
            cl = edit_movable
        else:
            cl = edit_class
        return cl,djp.view.appmodel.deleteurl(djp.request, djp.instance)
    
    def footer(self, djp, cblock, html):
        return djp.view.get_preview(djp.request, djp.instance, self.url)
             
        

class ChangeContentView(views.ChangeView):
    '''View class for managing inline editing of a content block.
    '''    
    def get_preview(self, request, instance, url, plugin = None):
        '''Render a plugin and its wrapper for preview within a div element'''
        try:
            djpview = request.DJPCMS.root.djp(request, url[1:])
            preview_html = instance.render(djpview,
                                           plugin = plugin)
        except Exception as e:
            preview_html = '%s' % e
        return mark_safe('<div id="%s">%s</div>' % (instance.pluginid('preview'),preview_html))
    
    def __get_form(self, djp, force_prefix = True, **kwargs):
        '''Get the contentblock editing form
        This form is composed of two parts,
        one for choosing the plugin type,
        and one for setting the plugin options
        '''
        if url:
            initial = initial if initial is not None else {}
            initial['url'] = url
        else:
            initial = None
        fw = super(ChangeContentView,self).get_form(djp,
                                                    initial = initial,
                                                    force_prefix = True,
                                                    **kwargs)
        if all:
            instance = djp.instance
            pform,purl = self.get_plugin_form(djp, instance.plugin)
            id = instance.pluginid('options')
            if pform:
                if isinstance(pform,FormType):
                    pform = HtmlForm(pform)
                #layout.id = id
                fw.add(pform)
            else:
                # No plugin
                fw.add('<div id="%s"></div>' % id)
            sub = SubmitInput(value = "edit", name = 'edit_content').render(djp)
            id = instance.pluginid('edit')
            cl = '' if purl else ' class="djphide"'
            #fw.inputs.append('<span id="{0}"{1}>{2}</span>'.format(id,cl,sub))
        return fw
        
    def get_plugin_form(self, djp, plugin, prefix):
        '''Retrieve the plugin editing form. If ``plugin`` is not ``None``,
it returns a tuple with the plugin form and the url
for editing plugin contents.'''
        if plugin:
            instance = djp.instance
            args     = None
            if instance.plugin == plugin:
                args = instance.arguments
            pform = plugin.get_form(djp, args, prefix = prefix)
            if pform:
                # Remove the tag since this form is injected in the block form.
                pform.tag = None
                purl = djp.view.appmodel.pluginurl(djp.request, instance)
                return (pform,purl)
        return (None,None)
            
    def edit_block(self, request):
        return jhtmls(identifier = '#' + self.instance.pluginid(),
                      html = self.instance.plugin_edit_block(request))
    
    def ajax__container_type(self, djp):
        return self.handle_content_block_changes(djp, commit = False)
    
    def ajax__plugin_name(self, djp):
        return self.handle_content_block_changes(djp, commit = False)
    
    def default_post(self, djp):
        return self.handle_content_block_changes(djp)
        
    def ajax__edit_content(self, djp):
        pluginview = self.appmodel.getview('plugin')
        return pluginview.default_post(pluginview(djp.request, instance = djp.instance))
    
    def block_from_edit_id(self, id):
        id = '-'.join(id.split('-')[1:])
        return self.model.block_from_html_id(id)
        
    def ajax__rearrange(self, djp):
        '''Move the content block to a new position and updates all html attributes'''
        request = djp.request
        contentblock = djp.instance
        data   = request.data_dict
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
            if block != contentblock.block or contentblock.position != newposition:
                # modify positions in the drop box
                for bc in self.model.objects.filter(page = contentblock.page, block = block):
                    if bc.position < newposition:
                        continue
                    bc.position += 1
                    bc.save()
                contentblock.position = newposition
                contentblock.block = block
                contentblock.save()
                #update_page(self.model,page)
            return jempty()
        except Exception as e:
            return jerror('Could not find target block. {0}'.format(e))
    
    def render(self, djp, url):
        formhtml = self.get_form(djp,
                                 initial = {'url': url},
                                 force_prefix = True)
        form = formhtml.form
        prefix = form.prefix
        pform,purl = self.get_plugin_form(djp, djp.instance.plugin, prefix)
        html = '' if not pform else pform.render(djp)
        return formhtml.render(djp, plugin = html)
    
    def handle_content_block_changes(self, djp, commit = True):
        '''View called when changing the content plugin values.
The instance.plugin object is maintained but its fields may change.'''
        instance = djp.instance
        request = djp.request
        fhtml = self.get_form(djp, method = request.method, force_prefix = True)
        form = fhtml.form
        prefix = form.prefix
        layout = fhtml.layout
        if not form.is_valid():
            return layout.json_messages(form)        
        data = form.cleaned_data
        url = data['url']
        pform,purl = self.get_plugin_form(djp, data['plugin_name'], prefix)
        
        if commit and pform and not pform.is_valid():
            return layout.json_messages(pform.form)
        
        if pform:
            instance.arguments = instance.plugin.save(pform.form)
            pform.tag = None
            plugin_options = pform.render(djp)
        else:
            plugin_options = '' if not pform else pform.render(djp)
        instance = form.save(commit = commit)
        jquery = jhtmls(identifier = '.' + PLUGIN_DATA_FORM_CLASS,
                        html = plugin_options,
                        alldocument = False)
        preview = self.get_preview(request, instance, url)
        jquery.add('#%s' % instance.pluginid('preview'), preview)
        
        if commit:
            form.add_message("Plugin changed to %s" % instance.plugin.description)
            
        jquery.update(layout.json_messages(form))
        return jquery

        
class DeleteContentView(views.DeleteView):
    
    def default_post(self, djp):
        instance = djp.instance
        block  = instance.block
        jquery = jcollection()
        blockcontents = self.model.objects.for_page_block(instance.page, block)
        if instance.position == len(blockcontents) - 1:
            return jquery
        
        jatt   = jattribute()
        pos    = 0
        for b in blockcontents:
            if b == instance:
                jquery.append(jremove('#'+instance.htmlid()))
                b.delete()
                continue
            if b.position != pos:
                b.position = pos
                b.save()
            pos += 1
        jquery.append(jatt)

        if djp.request.is_ajax():
            return jquery
        else:
            refer = sjp.request.environ.get('HTTP_REFERER')
            return self.redirect(refer)
    

class EditPluginView(views.ChangeView):
    '''View class for editing the content of a plugin. Not all plugins have an editing view.
The url is given by the ContentBlocks models
    '''
    _methods = ('post',)
    
    def get_form(self, djp, **kwargs):
        instance = djp.instance
        p = instance.plugin
        if p:
            return p.edit(djp, instance.arguments, **kwargs)
                
    
    def default_post(self, djp):
        data = dict(djp.request.POST.items())
        prefix = data['_prefixed']
        is_ajax = djp.request.is_ajax()
        try:
            initial = {'url':data['{0}-url'.format(prefix)]}
            f = self.get_form(djp, initial = initial, withdata = False)
        except PermissionDenied as e:
            return jerror(str(e))
        
        if f:
            uni = UniForm(f,
                          request  = djp.request,
                          action = djp.url).addClass(djp.css.ajax).addClass('editing')
            if is_ajax:
                d = dialog(hd = unicode(f.instance),
                           bd = uni.render(djp),
                           modal  = True,
                           width  = djp.settings.CONTENT_INLINE_EDITING.get('width','auto'),
                           height = djp.settings.CONTENT_INLINE_EDITING.get('height','auto'))
                d.addbutton('Ok', url = djp.url, func = 'save')
                d.addbutton('Cancel', func = 'cancel')
                d.addbutton('Save', url = djp.url, func = 'save', close = False)
                return d
            else:
                #todo write the non-ajax POST view
                pass
        else:
            return jerror('Nothing selected. Cannot edit.')
    
    def ajax__save(self, djp):
        f = self.get_form(djp)
        if f.is_valid():
            f.save()
            instance = djp.instance
            editview = self.appmodel.getview('edit')
            return editview.get_preview_response(djp,f.cleaned_data['url'])
        else:
            return f.json_errors()
        


class ContentSite(views.ModelApplication):
    '''AJAX enabled :class:`djpcms.views.ModelApplication` for changing
content in a content block.'''
    has_plugins = False
    search      = views.SearchView()
    view        = views.ViewView()
    change      = ChangeContentView()
    delete      = DeleteContentView()
    plugin      = EditPluginView(regex = 'plugin', parent = 'change')
    
    def submit(self, *args, **kwargs):
        return [SubmitInput(value = "save", name = '_save')]
    
    def remove_object(self, obj):
        bid = obj.htmlid()
        if self.model.objects.delete_and_sort(obj):
            return bid
        
    def pluginurl(self, request, obj):
        p = obj.plugin
        if not p or not p.edit_form:
            return
        view = self.getview('plugin')
        if view and self.has_change_permission(request, obj):
            djp = view(request, instance = obj)
            return djp.url

    def blockhtml(self, djp, instance, editview, wrapper):
        '''A content block rendered in editing mode'''
        editdjp = editview(djp.request, instance = instance)
        djp.media += editdjp.media
        editdjp.media = djp.media
        html = editview.render(editdjp, djp.url)
        return wrapper(editdjp,instance,html)
            
    def blocks(self, djp, page, blocknum):
        '''Return a generator of edit blocks.
        '''
        blockcontents = self.model.objects.for_page_block(page, blocknum)
        request  = djp.request
        url      = djp.url
        editview = self.getview('change')
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
            yield self.blockhtml(djp, b, editview, wrapper)
            
        # Create last block
        if last == None:
            last = self.model(page = page, block = blocknum, position = pos)
            last.save()
            yield self.blockhtml(djp, last, editview, wrapper)