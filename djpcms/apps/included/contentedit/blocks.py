'''
Application for handling inline editing of blocks
The application derives from the base appsite.ModelApplication
and defines several ajax enabled sub-views 
'''
from py2py3 import range

from djpcms import forms
from djpcms.forms import FormType, HtmlForm, SubmitInput, HtmlWidget
from djpcms.core.page import block_htmlid
from djpcms.utils.translation import gettext as _
from djpcms.core.exceptions import PermissionDenied
from djpcms.template import loader
from djpcms.utils.ajax import jhtmls, jremove, dialog, jempty
from djpcms.utils.ajax import jerror, jattribute, jcollection
from djpcms.plugins.extrawrappers import CollapsedWrapper
from djpcms import views

from .layout import ContentBlockHtmlForm

dummy_wrap = lambda d,b,x : x


edit_class = 'edit-block'
movable_class = 'movable'
edit_movable = edit_class + ' ' + movable_class


# Content wrapper in editing mode.
# Only called by content_view (function above)
class EditWrapperHandler(CollapsedWrapper):
    '''Wrapper for editing content
    '''
    auto_register = False
    def __init__(self, url):
        self.url = url
        
    def __call__(self, djp, cblock, html):
        return self.wrap(djp, cblock, html)
    
    def title(self, cblock):
        return ''
    
    def id(self, cblock):
        return cblock.htmlid()
    
    def _wrap(self, djp, cblock, html):
        if cblock.plugin_name:
            cl = edit_movable
        else:
            cl = edit_class
        return cl,djp.view.appmodel.deleteurl(djp.request, djp.instance)
    
    def footer(self, djp, cblock, html):
        return djp.view.get_preview(djp.request, djp.instance, self.url)
             
        
# Application view for handling change in content block internal plugin
# It handles two different Ajax interaction with the browser 
class ChangeContentView(views.ChangeView):
    '''View class for managing inline editing of a content block.
    The url is given by the ContentBlocks models
    '''
    _methods = ('post',)
        
    def render(self, djp, url = None):
        return self.get_form(djp, url = url).render(djp)
    
    def get_preview(self, request, instance, url, wrapped = True, plugin = None):
        try:
            djpview = request.DJPCMS.root.djp(request, url[1:])
            preview_html = instance.render(djpview,
                                           plugin = plugin)
        except Exception as e:
            preview_html = '%s' % e
        if wrapped:
            return loader.mark_safe('<div id="%s">%s</div>' % (instance.pluginid('preview'),preview_html))
        else:
            return preview_html
    
    def get_form(self, djp, all = True, url = None, initial = None, **kwargs):
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
        
    def get_plugin_form(self, djp, plugin, withdata = True):
        '''Retrieve the plugin editing form. If ``plugin`` is not ``None``,
it returns a tuple with the plugin form and the url
for editing plugin contents.'''
        if plugin:
            instance = djp.instance
            args     = None
            if instance.plugin == plugin:
                args = instance.arguments
            pform = plugin.get_form(djp,args,withdata=withdata)
            if pform:
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
    
    def __ajax__plugin_name(self, djp):
        
        '''
        Ajax post view function which handle the change of pluging
        within one html block. It return JSON serializable object 
        '''
        form = self.get_form(djp).form
        if form.is_valid():
            url        = form.cleaned_data['url']
            new_plugin = form.cleaned_data['plugin_name']
            pform,purl = self.get_plugin_form(djp, new_plugin, False)
            if pform:
                html = UniForm(pform,tag=False).render(djp)
            else:
                html = ''
            instance = djp.instance
            preview = self.get_preview(djp.request, instance, url)
            data = jhtmls(identifier = '#%s' % instance.pluginid('options'), html = html)
            preview = self.get_preview(djp.request, instance, url, plugin = new_plugin, wrapped = False)
            data.add('#%s' % instance.pluginid('preview'), preview)
            id = instance.pluginid('edit')
            if callable(new_plugin.edit_form):
                data.add('#%s' % id, type = 'show')
            else:
                data.add('#%s' % id, type = 'hide')
            return data
        else:
            return form.json_errors()
        
    def ajax__edit_content(self, djp):
        pluginview = self.appmodel.getview('plugin')
        return pluginview.default_post(pluginview(djp.request, instance = djp.instance))
        
    def ajax__rearrange(self, djp):
        '''Move the content block to a new position and updates all html attributes'''
        request = djp.request
        contentblock = djp.instance
        data   = request.data_dict
        try:            
            previous = data.get('previous',None)
            if previous:
                block = self.model.block_from_html_id(previous)
                pos = block.position
                newposition = pos + 1
            else:
                nextv = data.get('next',None)
                if nextv:
                    block = self.model.block_from_html_id(nextv)
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
    
    def handle_content_block_changes(self, djp, commit = True):
        '''View called when changing the content plugin values.
The instance.plugin object is maintained but its fields may change.'''
        fhtml = self.get_form(djp)
        form = fhtml.form
        layout = fhtml.layout
        
        if not form.is_valid():
            if is_ajax:
                return layout.json_messages(form)
            else:
                return djp.view.handle_response(djp)
        
        instance = djp.instance
        request = djp.request
        cd = form.cleaned_data
        plugin = cd['plugin_name']
        container = cd['container_type']
        url = cd['url']
        pform,purl = self.get_plugin_form(djp, plugin, withdata = commit)
        
        if commit and pform and not pform.is_valid():
            return layout.json_messages(pform)
            
        instance = form.save(commit = commit)
        preview = self.get_preview(request, instance, url)
        jquery = jhtmls(identifier = '#%s' % instance.pluginid('preview'),
                        html = preview)
        
        if commit:
            form.add_message("Plugin changed to %s" % instance.plugin.description)
        
        jquery.update(layout.json_messages(form))
        return jquery
    
        if form.is_valid():
            # save the plugin
            instance   = form.save(commit = False)
            pform = None
            #pform = None if len(forms) == 1 else forms[1]
            instance.arguments = instance.plugin.save(pform)
            instance.save()
            # We now serialize the argument form
            if is_ajax:
                page = instance.page
                block = instance.block
                preview = self.get_preview(request, instance, url,  wrapped = False)
                jquery = jhtmls(identifier = '#%s' % instance.pluginid('preview'), html = preview)
                form.add_message("Plugin changed to %s" % instance.plugin.description)
                jquery.update(layout.json_messages(form))
                cblocks = self.model.objects.filter(page = page, block = block)
                if instance.position == cblocks.count()-1:
                    b = page.get_block(block)
                    editdjp = self(request, instance = b)
                    html = self.render(editdjp, url = url)
                    wrapper  = EditWrapperHandler(url)
                    html = wrapper(editdjp,b,html)
                    jquery.add('#'+block_htmlid(page.id,block),html,'append')
                return jquery
            else:
                raise NotImplemented 
        else:
            if is_ajax:
                return form.json_errors()
            else:
                raise NotImplemented
            
    def get_preview_response(self, djp, url):
        instance = djp.instance
        preview = self.get_preview(djp.request, instance, url,  wrapped = False)
        return jhtmls(identifier = '#%s' % instance.pluginid('preview'), html = preview)
        
        
class DeleteContentView(views.DeleteView):
    
    def default_post(self, djp):
        instance = djp.instance
        block  = instance.block
        jquery = jcollection()
        blockcontents = self.model.objects.for_page_block(instance.page, block)
        if instance.position == blockcontents.count() - 1:
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
    
    def get_form(self, djp, withdata = True, initial = None, **kwargs):
        instance = djp.instance
        p = instance.plugin
        if p:
            return p.edit(djp, instance.arguments, initial = initial, withdata = withdata)
                
    
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
        editdjp = editview(djp.request, instance = instance)
        djp.media += editdjp.media
        editdjp.media = djp.media
        html = editview.render(editdjp, url = djp.url)
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