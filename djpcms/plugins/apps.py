import json

from djpcms import forms, html
from djpcms.forms.layout import DivFormElement, FormLayout, nolabel, SubmitElement
from djpcms.template import loader
from djpcms.core.orms import mapper
from djpcms.plugins import DJPplugin
from djpcms.http import QueryDict
from djpcms.utils.text import nicename


def registered_models(bfield,required = True):
    '''Generator of model Choices'''
    form = bfield.form
    site = form.request.DJPCMS.site
    if not required:
        yield ('','----------')
    for model,app in site._registry.items():
        if not app.hidden:
            id = getattr(mapper(model),'hash',None)
            if id:
                nice = '{0} from {1}'.format(nicename(model._meta.name),
                                             nicename(model._meta.app_label))
                yield (id,nice)


def get_contet_choices(bfield):
    model = bfield.form.model
    if not model:
        raise StopIteration
    else:
        request = bfield.form.request
        if request:
            info = request.DJPCMS
            appmodel = info.site.for_model(model, all = True)
            if appmodel:
                sdjp = appmodel.getview('search')(request)
                return appmodel.basequery(sdjp) 
        
        return mapper(model).all()
    
    
class ForModelForm(forms.Form):
    for_model   = forms.ChoiceField(required = False,
                            choices = lambda x : sorted(registered_models(x,False),
                                                        key = lambda y : y[1]))
    
    def clean_for_model(self, mhash):
        if mhash:
            try:
                return self.request.DJPCMS.site.for_hash(mhash,safe=False)
            except Exception as e:
                raise forms.ValidationError(str(e))


class ModelItemListForm(ForModelForm):
    max_display = forms.IntegerField(initial = 10)
    pagination  = forms.BooleanField(initial = False)
    filter = forms.CharField(required = False)
    exclude = forms.CharField(required = False)
    order_by = forms.CharField(required = False)
    display_if_empty = forms.BooleanField(initial = False)


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
    layout = forms.ChoiceField(choices = (('horizontal','horizontal'),
                                          ('vertical','vertical')))
    exclude = forms.CharField(max_length=600,required=False)
    

class ContentForm(forms.Form):
    content = forms.ChoiceField(choices = get_contet_choices,
                                autocomplete = True)

#
#___________________________________________ A CLASSY SEARCH FORM
class SearchForm(forms.Form):
    '''
    A simple search form used by plugins.apps.SearchBox.
    The search_text name will be used by SearchViews to handle text search
    '''
    q = forms.CharField(required = False,
                        widget = html.TextInput(default_class = 'classy-search autocomplete-off',
                                                title = 'Enter your search text'))


SearchSubmit = html.WidgetMaker(tag = 'div',
                                default_class='cx-submit',
                                inner = html.Widget('input:submit',
                                                    cn='cx-search-btn '+forms.NOBUTTON,
                                                    title = 'Search').render())

HtmlSearchForm = forms.HtmlForm(
        SearchForm,
        inputs = [SearchSubmit],
        layout = FormLayout(
                    SubmitElement(tag = None),
                    DivFormElement('q', default_class = 'cx-input'),
                    tag = 'div',
                    default_style = nolabel,
                    default_class = 'cx-search-bar'
            )
)
#
#______________________________________________ PLUGINS

class SearchBox(DJPplugin):
    '''A text search for a model rendered as a nice search input.
    '''
    name = 'search-box'
    description = 'Search your Models'
    form = SearchModelForm
    
    def render(self, djp, wrapper, prefix,
               for_model = None, method = 'get',
               tooltip = None, ajax = False,
               **kwargs):
        engine = djp.site.search_engine
        if not engine:
            raise ValueError('No search engine installed with site. Cannot add search plugin.\
 You need to install one! Check documentation on how to do it.')
        request = djp.request
        data = request.GET if method == 'get' else request.POST
        w = HtmlSearchForm(data = data or None)
        if tooltip:
            w.form.dfields['q'].title = tooltip
        path = engine.search_url(for_model)
        w.addAttr('action',engine.path).addAttr('method',method)
        if ajax:
            w.addClass(forms.AJAX)
        return w.render(djp)



class RenderObject(DJPplugin):
    '''Render a database object'''
    virtual = True
    description = 'Display your content'
    form = ContentForm
    
    def get_object(self, content):
        if content and self.for_model:
            return mapper(self.for_model).get(id = content)
        
    def render(self, djp, wrapper, prefix, content = None, **kwargs):
        obj = self.get_object(content)
        if obj:
            appmodel = djp.site.for_model(self.for_model, all = True)
            if appmodel:
                view = appmodel.getview('view')
                return view(djp.request, instance = obj).render()
            else:
                return str(obj)
        else:
            return ''
        
    def edit_url(self, djp, args = None):
        initial = self.arguments(args)
        obj = self.get_object(initial.get('content',None))
        return djp.site.get_url(self.for_model, 'change', instance = obj, all = True)
      
    

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
    
    
class ModelItemsList(DJPplugin):
    '''Display filtered items for a Model.'''
    name = 'model-items'
    description    = 'Filtered Items list for a model'
    form           = ModelItemListForm
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
    
    def query(self, val):
        if val:
            try:
                return dict(QueryDict(val).items())
            except:
                pass
        return {}
    
    def render(self, djp, wrapper, prefix,
               for_model = None, max_display = 5,
               pagination = False, filter = None,
               exclude = None, order_by = None,
               display_if_empty = False,
               **kwargs):
        appmodel = djp.site.for_hash(for_model,safe=False,all=True)
        qs = appmodel.basequery(djp).filter(**self.query(filter))\
                                    .exclude(**self.query(exclude))\
                                    .sort_by(order_by)        
        max_display = max(int(max_display),1)
        items = qs[0:max_display]
        if not items:
            return ''
        templates = self.get_templates(appmodel.mapper,'list')
        ctx = {'items': self.datagen(appmodel, djp, wrapper, items)}
        return loader.render(templates,ctx)

    
