from djpcms import forms, html
from djpcms.forms.layout import DivFormElement, FormLayout, nolabel
from djpcms.template import loader
from djpcms.core.orms import mapper
from djpcms.plugins import DJPplugin


def registered_models(bfield):
    '''Generator of model Choices'''
    form = bfield.form
    site = form.request.DJPCMS.site
    for model,app in site._registry.items():
        if not app.hidden:
            id = mapper(model).hash
            yield id,str(model._meta)
    
    
class ForModelForm(forms.Form):
    for_model   = forms.ChoiceField(choices = registered_models)
    
    def clean_for_model(self, mhash):
        try:
            return self.request.DJPCMS.site.for_hash(mhash,safe=False)
        except Exception as e:
            raise forms.ValidationError(str(e))


class LatestItemForm(ForModelForm):
    max_display = forms.IntegerField(initial = 10)
    pagination  = forms.BooleanField(initial = False)


class FormModelForm(ForModelForm):
    method      = forms.ChoiceField(choices = (('get','get'),('post','post')),
                                    initial = 'get')
    ajax        = forms.BooleanField(initial = False)


class SearchModelForm(FormModelForm):
    tooltip  = forms.CharField(required = False, max_length = 50)


class FilterModelForm(FormModelForm):
    pass


class ModelLinksForm(forms.Form):
    asbuttons = forms.BooleanField(initial = True, label = 'as buttons')
    layout = forms.ChoiceField(choices = (('horizontal','horizontal'),('vertical','vertical')))
    exclude = forms.CharField(max_length=600,required=False)
    


#
#___________________________________________ A CLASSY SEARCH FORM
class SearchForm(forms.Form):
    '''
    A simple search form used by plugins.apps.SearchBox.
    The search_text name will be used by SearchViews to handle text search
    '''
    q = forms.CharField(required = False,
                        widget = html.TextInput(cn = 'classy-search autocomplete-off',
                                                title = 'Enter your search text'))

SearchSubmit = html.HtmlWrap(tag = 'div', cn='cx-submit',
                             inner = html.SubmitInput(cn='cx-search-btn '+forms.NOBUTTON,
                                                      title = 'Search').render())
HtmlSearchForm = forms.HtmlForm(
        SearchForm,
        inputs = [SearchSubmit],
        layout = FormLayout(
                    DivFormElement('q',
                                   default_style = nolabel,
                                   cn = 'cx-input'),
                    template = ('search_form.html',
                                'djpcms/components/search_form.html')
            )
)
#
#______________________________________________ PLUGINS

class SearchBox(DJPplugin):
    '''A text search for a model rendered as a nice search input.
    '''
    name = 'search-box'
    description = 'Search a Model' 
    template_name = ('search_form.html',
                     'djpcms/components/search_form.html')
    form = SearchModelForm
    
    def render(self, djp, wrapper, prefix,
               for_model = None, method = 'get',
               tooltip = None, ajax = False,
               **kwargs):
        site = djp.site
        request = djp.request
        appmodel = site.for_hash(for_model,safe=False)
        search_url = appmodel.searchurl(request)
        if search_url:
            data = request.GET if method == 'get' else request.POST
            f = HtmlSearchForm(data = data or None)
            if tooltip:
                f.dfields['q'].title = tooltip
            w =  HtmlSearchForm.widget(f,
                                       inputs = HtmlSearchForm.default_inputs, 
                                       action = search_url,
                                       method = method)
            if ajax:
                w.addClass(forms.AJAX)
            return w.render()


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
    
    
class ModelLinks(DJPplugin):
    name = 'model-links'
    description = 'Links for a model'
    template_name = ('links.html',
                     'djpcms/components/links.html')
    form = ModelLinksForm
    
    def get_links(self, djp, exclude, asbuttons):
        return djp.view.appmodel.links(djp, asbuttons=asbuttons, exclude=exclude)
    
    def render(self, djp, wrapper, prefix, layout = 'horizontal',
               asbuttons = True, exclude = '', **kwargs):
        exclude = exclude.split(',')
        links = self.get_links(djp, exclude, asbuttons)
        if links['links']:
            links['layout'] = layout
            return loader.render(self.template_name, links)
        else:
            return ''
    
    
class ObjectLinks(ModelLinks):
    name = 'edit-object'
    description = 'Links for a model instance'
    form = ModelLinksForm
    
    def get_links(self, djp, exclude, asbuttons):
        return djp.view.appmodel.object_links(djp,
                                              djp.instance,
                                              asbuttons=asbuttons,
                                              exclude=exclude)
    
    
class LatestItems(DJPplugin):
    '''Display the latest items for a Model.'''
    name = 'latest-items'
    description    = 'Latest items for a model'
    form           = LatestItemForm
    template_names = {
                      'list': ('djpcms/plugins/latestitems/list.html',),
                      'item': ('djpcms/plugins/latestitems/item.html',)
                      }       
    
    def get_templates(self, opts, name):
        template = '{0}/{1}/latestitems/{2}.html'.format(opts.app_label,
                                                         opts.module_name,
                                                         name)
        return (template,) + self.template_names[name]
        
    def datagen(self, appmodel, djp, wrapper, items):
        templates = self.get_templates(appmodel.mapper,'item')
        for obj in items:
            content = appmodel.object_content(djp, obj)
            yield loader.render(templates,content)
            
    def render(self, djp, wrapper, prefix,
               for_model = None, max_display = 5,
               pagination = False, **kwargs):
        site = djp.site
        appmodel = site.for_hash(for_model,safe=False)
        data = appmodel.orderquery(appmodel.basequery(djp))
        max_display = max(max_display,1)
        items = data[0:max_display]
        if not items:
            return ''
        templates = self.get_templates(appmodel.mapper,'list')
        ctx = {'items': self.datagen(appmodel, djp, wrapper, items)}
        return loader.render(templates,ctx)

    
