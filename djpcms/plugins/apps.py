from djpcms import forms, html, views, VIEW
from djpcms.plugins import DJPplugin
from djpcms.core.http import query_from_string
from djpcms.utils.text import nicename


def registered_models(bfield, required = True):
    '''Generator of model Choices'''
    form = bfield.form
    request = form.request
    if not required:
        yield ('','----------')    
    if request:
        root = form.request.view.root
        models = set()
        for app in root.applications():
            if app.mapper and app.model not in models:
                models.add(app.model)
                id = app.mapper.hash
                if id and request.has_permission(VIEW,app.model):
                    yield (id,str(app.mapper))


def get_contet_choices(bfield):
    model = bfield.form.model
    if not model:
        raise StopIteration
    else:
        request = bfield.form.request
        if request:
            appmodel = request.view.site.for_model(model)
            if appmodel:
                sdjp = appmodel.getview('search')(request)
                return appmodel.basequery(sdjp) 
        
        return mapper(model).all()
    
    
class ForModelForm(forms.Form):
    for_model = forms.ChoiceField(
                      required = False,
                      #widget = html.Select(default_class = 'ajax'),
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
#______________________________________________ PLUGINS

class RenderObject(DJPplugin):
    '''Render an instance of a model using the
:attr:`Application.instance_view`.'''
    virtual = True
    description = 'Display your content'
    form = ContentForm
    
    def get_object(self, content):
        if content and self.for_model:
            return mapper(self.for_model).get(id = content)
        
    def render(self, request, wrapper, prefix, content = None, **kwargs):
        obj = self.get_object(content)
        if obj:
            appmodel = request.view.site.for_model(self.for_model)
            if appmodel:
                view = appmodel.instance_view
                if view:
                    return request.for_view(view, instance = obj).render()
            return str(obj)
        else:
            return ''
    
    
class ApplicationLinks(DJPplugin):
    '''Display links for an application.'''
    name = 'model-links'
    description = 'Links for a model'
    template_name = ('links.html',
                     'djpcms/components/links.html')
    asbuttons_class = 'asbuttons'
    form = ModelLinksForm
    
    def render(self, request, wrapper, prefix, layout = 'horizontal',
               asbuttons = True, exclude = '', include = '',
               for_instance = False, **kwargs):
        appmodel = request.view.appmodel
        if not appmodel:
            return
        exclude = None if not exclude else exclude.split(',')
        include = None if not include else include.split(',')
        instance = None if not for_instance else request.instance
        asbuttons = self.asbuttons_class if asbuttons else None
        links = views.application_links(
                            views.application_views(request,
                                                    exclude = exclude,
                                                    include = include,
                                                    instance = instance),
                            asbuttons = asbuttons)
        if appmodel.mapper:
            name = appmodel.mapper.class_name(appmodel.model)
        else:
            name = None
        if links:
            return html.Widget('ul', (l[1] for l in links), cn = name)\
                       .addClass('model-links')\
                       .addClass(layout)\
                       .addClass(asbuttons)\
                       .render(request)
    
    
def attrquery(heads,query):
    for k in query:
        v = query[k]
        if k in heads:
            k = heads[k].attrname
        yield k,v
    
    
class ModelItemsList(DJPplugin):
    '''Filter a model according to editable criteria snd displays a
certain number of items as specified in the max display input.'''
    name = 'model-items'
    description = 'Filtered items for a model'
    form = ModelItemListForm
    
    def render(self, request, block, prefix,
               for_model = None, max_display = 5,
               pagination = False, filter = None,
               exclude = None, order_by = None,
               text_search = None, headers = None,
               display_if_empty = '',
               table_footer = False,
               **kwargs):
        instance = request.instance
        request = request.for_model(for_model)
        if request is None:
            return ''
        view = request.view
        appmodel = view.appmodel 
        load_only = ()
        thead = None
        appheads = request.pagination.headers
        
        if headers:
            thead = []
            for head in headers.split():
                if head in appheads:
                    thead.append(appheads[head])
        
        # Ordering
        if order_by:
            decr = False
            if order_by.startswith('-'):
                order_by = order_by[1:]
                decr = True
            order_by = html.attrname_from_header(appheads,order_by)
            if decr:
                order_by = '-{0}'.format(order_by)
                
        qs = view.query(request, instance = instance)
        if text_search:
            qs = qs.search(text_search)
        qs = qs.filter(**dict(attrquery(appheads,query_from_string(filter))))\
               .exclude(**dict(attrquery(appheads,query_from_string(exclude))))\
               .sort_by(order_by)\
               .load_only(*appmodel.load_fields(thead))
               
        max_display = max(int(max_display),1)
        items = qs[0:max_display]
        if not items:
            return display_if_empty
        
        if thead:
            pagination = html.Pagination(
                            thead, 
                            footer = table_footer,
                            html_data =  {'options': {'sDom':'t'}})
            return pagination.widget(
                    appmodel.table_generator(request, thead, items),
                    title = block.title, appmodel = appmodel).render(request)
        else:
            w = html.Widget('div', cn = 'filtered-list')\
                    .addClass(appmodel.mapper.class_name())
            render_object = appmodel.render_object
            inner = '\n'.join(render_object(request, item, 'list')\
                              for item in items)
            return w.render(request,inner)

    
