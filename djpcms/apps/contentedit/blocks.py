from djpcms import forms, html, views, ajax
from djpcms.plugins import PLUGIN_DATA_FORM_CLASS
from djpcms.core.exceptions import PermissionDenied
from djpcms.forms.utils import get_redirect
from djpcms.plugins.extrawrappers import CollapsedWrapper

from .sitemap import underlying_response
from .layout import ContentBlockHtmlForm


__all__ = ['ContentApplication']


edit_class = 'edit-block ui-state-active'
movable_class = 'movable'
edit_movable = edit_class + ' ' + movable_class


# Content wrapper in editing mode.
# Only called by content_view (function above)
class EditWrapperHandler(CollapsedWrapper):
    '''a :class:`djpcms.plugins.DJPwrapper` for
editing content.'''
    always_render = True
    auto_register = False
    detachable = True

    def title(self, cblock):
        if cblock.plugin:
            return cblock.plugin.description
        else:
            return 'Content Editor'
    
    def id(self, cblock):
        return 'edit-{0}'.format(cblock.htmlid())
    
    def extra_class(self, request, block, html):
        if block.plugin_name:
            return edit_movable
        else:
            return edit_class
        
    def edit_menu(self, request, block):
        ul = html.Widget('ul')
        return ul.add(views.application_views_links(request,
                                                    asbuttons=False,
                                                    text=False,
                                                    include=('delete',)))
    
    def footer(self, request, cblock, html):
        return request.view.get_preview(request, request.instance)


class BlockChangeView(views.ChangeView):
    
    def block_from_edit_id(self, id):
        id = '-'.join(id.split('-')[1:])
        return self.model.block_from_html_id(id)


class ChangeContentView(BlockChangeView):
    '''View class for managing inline editing of a content block.
    '''
    def underlying(self, request):
        request = request.DJPCMS.request
        return underlying_response(request, request.instance)
    
    def get_preview(self, request, instance, plugin=None):
        '''Render a plugin and its wrapper for preview within a div element'''
        underlying = request.underlying()
        if underlying:
            try:
                preview_html = instance.widget(underlying, plugin=plugin)
            except Exception as e:
                preview_html = str(e)
        else:
            return 'Could not get preview'
        
        if preview_html not in (None,''):
            id = instance.pluginid('preview')
            return html.Widget('div', preview_html, id=id, cn='preview')
        else:
            return ''
        
    def plugin_form_container(self, instance, pform):
        pid = 'edit-plugin-data-{0}'.format(instance.id)
        return html.Widget('div', pform, id=pid, cn=PLUGIN_DATA_FORM_CLASS)
    
    def get_plugin_form(self, request, plugin, prefix, **kwargs):
        '''Retrieve the plugin editing form if ``plugin`` is not ``None``.'''
        if plugin:
            instance = request.instance
            args = None
            if instance.plugin == plugin:
                args = instance.arguments
            return plugin.get_form(request, args, prefix=prefix, **kwargs)
            
    def edit_block(self, request):
        return jhtmls(identifier = '#' + self.instance.pluginid(),
                      html = self.instance.plugin_edit_block(request))
    
    def ajax__container_type(self, request):
        '''Change container'''
        return self.post_response(request, commit = False, plugin_form = False)
    
    def ajax__plugin_name(self, request):
        '''Change plugin'''
        return self.post_response(request, commit=False)
        
    def ajax__edit_content(self, request):
        pluginview = self.appmodel.views.get('plugin')
        return pluginview.post_response(pluginview(request,
                                                   instance = request.instance))
        
    def ajax_get_response(self, request):
        return self.post_response(request, commit = False)
    
    def render(self, request, url = None):
        formhtml = self.get_form(request,
                                 initial = {'url': url},
                                 force_prefix = True)
        instance = request.instance
        plugin = instance.plugin
        if not plugin:
            return ''
        form = formhtml.form
        prefix = form.prefix
        plugin_form = self.get_plugin_form(request, instance.plugin, prefix)
        edit_url = plugin.edit_url(request,instance.arguments)
        if edit_url:
            edit_url = HtmlWrap('a',
                                cn = 'ajax button',
                                inner='Edit')\
                             .addAttr('href',edit_url)\
                             .addAttr('title','Edit plugin')\
                             .addData('method','get')
            formhtml.inputs.append(edit_url)
        wrapper = EditWrapperHandler()(request, instance, formhtml)
        # GET THE PLUGIN FORM IF NEEDED
        plugin = self.plugin_form_container(instance, plugin_form)
        return wrapper.render(request, {'plugin': plugin})
    
    def post_response(self, request, commit = True, plugin_form = True):
        '''View called when changing the content plugin values.
The instance.plugin object is maintained but its fields may change.'''       
        fhtml = self.get_form(request, withdata=True)
        form = fhtml.form
        
        if plugin_form:
            instance = request.instance
            prefix = form.prefix
            if not form.is_valid():
                if commit:
                    return fhtml.maker.json_messages(form)
                else:
                    return ajax.jhtmls() 
            data = form.cleaned_data
            pform = self.get_plugin_form(request,
                                         data['plugin_name'],
                                         prefix,
                                         withdata=commit)
            
            #plugin editing form is available
            if pform is not None:
                # if plugin form is bound and has error, returns the errors
                if pform.form.is_bound and not pform.is_valid():
                    return fhtml.maker.json_messages(pform.form)
                # Check what action to perform.
                action = forms.get_ajax_action(request.REQUEST)
                instance = form.save(commit = commit)
                plugin = instance.plugin
                if action:
                    action_func = getattr(plugin,'ajax__'+action,None)
                    if action_func:
                        value = forms.get_ajax_action_value(action,
                                                            request.REQUEST)
                        return action_func(request, value)
                # if committing, we get the arguments from the form
                if commit:
                    instance.arguments = plugin.save(pform.form)
                    instance.save()
                plugin_form = pform.render(request)
            else:
                instance = form.save(commit = commit)
                plugin_form = ''
            plugin_form = self.plugin_form_container(instance, plugin_form)
            jquery = ajax.jhtmls(identifier = '#' + plugin_form.attr('id'),
                                 html = plugin_form.render(request),
                                 type = 'replacewith')
        else:
            # we are just rerendering the plugin with a different wrapper
            instance = form.save(commit=commit)
            jquery = ajax.jhtmls()
            
        preview = self.get_preview(request, instance)
        jquery.add('#%s' % instance.pluginid('preview'),
                   html.render(request, preview))
        
        if plugin_form:
            if commit:
                form.add_message("Plugin changed to %s"\
                                 % instance.plugin.description)
            
            jquery.update(fhtml.maker.json_messages(form))
            
        return jquery

    def ajax__rearrange(self, request):
        '''Move the content block to a new position.'''
        contentblock = request.instance
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
    
    def post_response(self, request):
        instance = request.instance
        block  = instance.block
        jquery = ajax.jcollection()
        blockcontents = self.model.for_page_block(self.mapper,
                                                  instance.page, block)
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
            return self.redirect(get_redirect(request,force_redirect=True))


class ContentApplication(views.Application):
    '''AJAX enabled :class:`djpcms.views.Application` for changing
content in a content block.'''
    form = ContentBlockHtmlForm
    has_plugins = False
    pop_up = False
    url_bits_mapping = {'contentblock':'id'}
    
    search = views.SearchView()
    view = views.ViewView('<int:contentblock>/')
    change = ChangeContentView()
    delete = DeleteContentView()
    
    def on_bound(self):
        self.root.internals['BlockContent'] = self.mapper
    
    def submit(self, *args, **kwargs):
        return [html.Widget('input:submit', value = "save", name = '_save')]
    
    def remove_instance(self, instance):
        bid = instance.htmlid()
        instance.delete()
        return bid

    def blockhtml(self, request, instance, editpath, wrapper):
        '''A content block rendered in editing mode'''
        request = request.for_path(editpath, instance = instance)
        html = request.render(url = request.url)
        #layoutview = self.getview('layout')
        #html0 =  layoutview(djp.request, instance = instance).render()
        # html = html0 + html
        return wrapper(request,instance,html)
            
    def blocks(self, request, page, blocknum):
        '''Return a generator of edit blocks.
        '''
        blockcontents = self.model.for_page_block(self.mapper, page, blocknum)
        editpath = self.views.get('change').path
        wrapper  = EditWrapperHandler()
        Tot = len(blockcontents)
        pos = 0
        last = None
        # We update positions if needed
        for t, b in enumerate(blockcontents,1):
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
            yield self.blockhtml(request, b, editpath, wrapper)
            
        # Create last block
        if last == None:
            last = self.model(page = page, block = blocknum, position = pos)
            last.save()
            yield self.blockhtml(request, last, editpath, wrapper)
