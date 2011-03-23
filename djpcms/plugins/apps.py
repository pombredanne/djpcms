from djpcms import forms, html
from djpcms.template import loader
from djpcms.core.orms import mapper
from djpcms.plugins import DJPplugin
from djpcms.utils import gen_unique_id


def registered_models(bfield):
    '''Generator of model Choices'''
    form = bfield.form
    site = form.request.DJPCMS.site
    for model,app in site._registry.items():
        if not app.hidden:
            id = mapper(model).hash
            yield id,str(model._meta)
    
    
class SearchForm(forms.Form):
    '''
    A simple search form used by plugins.apps.SearchBox.
    The search_text name will be used by SearchViews to handle text search
    '''
    q = forms.CharField(required = False,
                        widget = html.TextInput(cn = 'classy-search autocomplete-off',
                                                title = 'Enter your search text'))

class ForModelForm(forms.Form):
    for_model   = forms.ChoiceField(choices = registered_models)
    
    def clean_for_model(self, mhash):
        try:
            info = self.request.DJPCMS
            model = info.root.model_from_hash[mhash]
            appmodel = info.site.for_model(model)
            return appmodel
        except:
            raise forms.ValidationError('Model has no application installed')


class LatestItemForm(ForModelForm):
    max_display = forms.IntegerField(initial = 10)
    pagination  = forms.BooleanField(initial = False)


class FormModelForm(ForModelForm):
    method      = forms.ChoiceField(choices = (('get','get'),('post','post')),
                                    initial = 'get')
    ajax        = forms.BooleanField(initial = False)


class SearchModelForm(FormModelForm):
    title  = forms.CharField(required = False, max_length = 50)


class FilterModelForm(FormModelForm):
    pass


class ModelLinksForm(forms.Form):
    asbuttons = forms.BooleanField(initial = True, label = 'as buttons')
    layout = forms.ChoiceField(choices = (('horizontal','horizontal'),('vertical','vertical')))
    exclude = forms.CharField(max_length=600,required=False)
    
#
#______________________________________________ PLUGINS

class SearchBox(DJPplugin):
    '''A search box for a model
    '''
    name = 'search-box'
    description = 'Search a Model' 
    form = SearchModelForm
    
    def render(self, djp, wrapper, prefix,
               for_model = None, method = 'get',
               title = None, **kwargs):
        if for_model:
            site = djp.site
            if for_model in site.root.model_from_hash:
                model = site.root.model_from_hash[for_model]
            else:
                raise ValueError('Content type %s not available' % for_model)
            appmodel = site.for_model(model)
            if appmodel:
                search_url = appmodel.searchurl(request)
                if search_url:
                    data = request.GET if method == 'get' else request.POST
                    #prefix = data.get("_prefixed",None)
                    #if not prefix:
                    #    prefix = gen_unique_id()
                    prefix = None
                    f = SearchForm(data = data, prefix = prefix)
                    if title:
                        f.fields['q'].widget.attrs['title'] = title
                    return loader.render_to_string(['search_form.html',
                                                    'bits/search_form.html',
                                                    'djpcms/bits/search_form.html'],
                                                    {'html':  f,
                                                     'prefix': prefix,
                                                     'title': title or 'Enter your search term',
                                                     'url':   search_url,
                                                     'method':method})
            else:
                raise ValueError('Model {0} has no application associated with it.'.format(model._meta))
        else:
            raise ValueError('Content type not available')


class ModelFilter(DJPplugin):
    '''Display filters for a model registered in the application registry.'''
    name = 'model-filter'
    description = 'Filter a model'
    form = FilterModelForm
    
    def render(self, djp, wrapper, prefix, for_model = None,
               ajax = False, method = 'get', **kwargs):
        appmodel, ok = app_model_from_ct(for_model)
        if not ok:
            return appmodel
        filters = appmodel.search_fields
        if not filters:
            return ''
        request = djp.request
        search_url = appmodel.searchurl(request)
        if not search_url:
            return ''
        model = appmodel.model
        initial = dict((request.GET or request.POST).items())
        form = forms.modelform_factory(model, appmodel.form, fields = filters, exclude = [])
        form.layout = FormLayout()
        f = UniForm(form(initial = initial),
                    method = method,
                    action = search_url)
        if ajax:
            f.addClass(djp.css.ajax)
        f.inputs.append(input(value = 'filter', name = '_filter'))
        return f.render()
    
    
class ObjectLinks(DJPplugin):
    name = 'edit-object'
    description = 'Links for a model instance'
    form = ModelLinksForm
    def render(self, djp, wrapper, prefix, layout = 'horizontal',
               asbuttons = True, exclude = '', **kwargs):
        try:
            exclude = exclude.split(',')
            links = djp.view.appmodel.object_links(djp,djp.instance, asbuttons=asbuttons, exclude=exclude)
            links['layout'] = layout
            if links['geturls'] or links['posturls']:
                return loader.render_to_string(['bits/editlinks.html',
                                                'djpcms/bits/editlinks.html'],
                                                links)
            else:
                return ''
        except:
            return ''
    
    
class ModelLinks(DJPplugin):
    name = 'model-links'
    description = 'Links for a model'
    form = ModelLinksForm
    def render(self, djp, wrapper, prefix, layout = 'horizontal',
               asbuttons = True, exclude = '', **kwargs):
        try:
            exclude = exclude.split(',')
            links = djp.view.appmodel.links(djp, asbuttons=asbuttons, exclude=exclude)
            links['layout'] = layout
            return loader.render_to_string(['bits/editlinks.html',
                                            'djpcms/bits/editlinks.html'],
                                            links)
        except:
            return ''
        

class LatestItems(DJPplugin):
    '''Display the latest items for a Model.'''
    name = 'latest-items'
    description    = 'Latest items for a model'
    form           = LatestItemForm
    template_names = {
                      'list': (
                               'plugins/latestitems/list.html',
                               'djpcms/plugins/latestitems/list.html',
                               ),
                      'item': (
                               'plugins/latestitems/item.html',
                               'djpcms/plugins/latestitems/item.html',
                               )
                       }       
    
    def get_templates(self, opts, name):
        template = '{0}/{1}/latestitems/{2}.html'.format(opts.app_label,
                                                         opts.module_name,
                                                         name)
        return (template,) + self.template_names[name]
        
    def datagen(self, appmodel, djp, wrapper, items):
        templates = self.get_templates(appmodel.opts,'item')
        for obj in items:
            content = appmodel.object_content(djp, obj)
            yield loader.render_to_string(templates,content)
            
    def render(self, djp, wrapper, prefix,
               for_model = None, max_display = 5,
               pagination = False, **kwargs):
        try:
            site = djp.site
            ct = ContentType.objects.get(id = for_model)
            model = ct.model_class()
            appmodel = site.for_model(model)
            if not appmodel:
                return ''
        except:
            return ''
        data = appmodel.orderquery(appmodel.basequery(djp))
        max_display = max(max_display,1)
        items = data[0:max_display]
        if not items:
            return ''
        templates = self.get_templates(appmodel.opts,'list')
        content = {'items': self.datagen(appmodel, djp, wrapper, items)}
        return loader.render_to_string(templates,
                                       content)

    
