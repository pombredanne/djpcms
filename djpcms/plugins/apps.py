import json

from djpcms import forms, html
from djpcms.forms.layout import DivFormElement, FormLayout, nolabel,\
                                 SubmitElement
from djpcms.template import loader
from djpcms.core.orms import mapper
from djpcms.plugins import DJPplugin
from djpcms.http import query_from_string
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
    for_model = forms.ChoiceField(
                      required = False,
                      widget = html.Select(default_class = 'ajax'),
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
    text_search = forms.CharField(required = False)
    filter = forms.CharField(required = False)
    exclude = forms.CharField(required = False)
    order_by = forms.CharField(required = False)
    headers = forms.CharField(required = False,
                              help_text = 'space separated list of headers.\
 If supplied, the widget will be displayed as a table with header given\
 by this input.')
    table_footer = forms.BooleanField(initial = False)
    display_if_empty = forms.BooleanField(initial = False)


class FormModelForm(ForModelForm):
    method      = forms.ChoiceField(choices = (('get','get'),('post','post')),
                                    initial = 'get')
    ajax        = forms.BooleanField(initial = False)


class SearchModelForm(FormModelForm):
    tooltip  = forms.CharField(required = False, max_length = 50)


class ModelLinksForm(forms.Form):
    asbuttons = forms.BooleanField(initial = True, label = 'as buttons')
    for_instance = forms.BooleanField()
    layout = forms.ChoiceField(choices = (('horizontal','horizontal'),
                                          ('vertical','vertical')))
    for_instance = forms.BooleanField()
    exclude = forms.CharField(max_length=600,required=False)
    include = forms.CharField(max_length=600,required=False)
    

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
    q = forms.CharField(
                required = False,
                widget = html.TextInput(
                        default_class = 'classy-search autocomplete-off',
                        title = 'Enter your search text'))


SearchSubmit = html.WidgetMaker(
                    tag = 'div',
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
            raise ValueError('No search engine installed with site.\
 Cannot add search plugin. You need to install one!\
 Check documentation on how to do it.')
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
        return djp.site.get_url(self.for_model, 'change',
                                instance = obj, all = True)
      
    
class ModelLinks(DJPplugin):
    name = 'model-links'
    description = 'Links for a model'
    template_name = ('links.html',
                     'djpcms/components/links.html')
    asbuttons_class = 'asbuttons'
    form = ModelLinksForm
    
    def render(self, djp, wrapper, prefix, layout = 'horizontal',
               asbuttons = True, exclude = '', include = '',
               for_instance = False, **kwargs):
        appmodel = djp.view.appmodel
        exclude = None if not exclude else exclude.split(',')
        include = None if not include else include.split(',')
        instance = None if not for_instance else djp.instance
        asbuttons = self.asbuttons_class if asbuttons else None
        links = html.application_links(
                            html.application_views(appmodel,
                                                   djp,
                                                   exclude = exclude,
                                                   include = include,
                                                   instance = instance),
                            asbuttons = asbuttons)
        name = appmodel.mapper.class_name(appmodel.model)
        if links:
            return html.List((l[1] for l in links), cn = name)\
                        .addClass('model-links')\
                        .addClass(layout)\
                        .addClass(asbuttons)\
                        .render(djp)
    
    
class ModelItemsList(DJPplugin):
    '''Display filtered items for a Model.'''
    name = 'model-items'
    description    = 'Filtered items for a model'
    form           = ModelItemListForm
    
    def render(self, djp, block, prefix,
               for_model = None, max_display = 5,
               pagination = False, filter = None,
               exclude = None, order_by = None,
               text_search = None, headers = None,
               display_if_empty = '',
               table_footer = False,
               **kwargs):
        if not for_model:
            return ''
        appmodel = djp.site.for_hash(for_model,safe=False,all=True)
        qs = appmodel.basequery(djp)
        if text_search:
            qs = qs.search(text_search)
        qs = qs.filter(**query_from_string(filter))\
               .exclude(**query_from_string(exclude))\
               .sort_by(order_by)        
        max_display = max(int(max_display),1)
        items = qs[0:max_display]
        if not items:
            return display_if_empty
        if headers:
            heads = appmodel.headers
            # fetch headers from appmodel
            thead = []
            for head in headers.split():
                if head in heads:
                    thead.append(heads[head])
        else:
            thead = None
                    
        if thead:
            data = {'options': {'sDom':'t'}}
            w = html.Table(thead,
                           body = appmodel.table_generator(djp, thead, qs),
                           appmodel = appmodel,
                           footer = table_footer,
                           data = data,
                           toolbox = False)
            return w.render(djp)
        else:
            w = html.Widget('div', cn = 'filtered-list')\
                    .addClass(appmodel.mapper.class_name())
            render_object = appmodel.render_object
            inner = '\n'.join(render_object(djp, item, 'list')\
                              for item in items)
            return w.render(djp,inner)

    
