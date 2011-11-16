from djpcms import forms, html, views
from djpcms.core.orms import mapper
from djpcms.plugins import DJPplugin
from djpcms.core.http import query_from_string
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
        links = views.application_links(
                            views.application_views(appmodel,
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
    
    
def attrquery(heads,query):
    for k in query:
        v = query[k]
        if k in heads:
            k = heads[k].attrname
        yield k,v
    
    
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
        instance = djp.instance
        appmodel = djp.site.for_hash(for_model,safe=False,all=True)
        djp = appmodel.root_view(djp.request,**djp.kwargs)
        heads = appmodel.headers
        if order_by:
            decr = False
            if order_by.startswith('-'):
                order_by = order_by[1:]
                decr = True
            order_by = html.attrname_from_header(heads,order_by)
            if decr:
                order_by = '-{0}'.format(order_by)
        qs = djp.basequery(instance = instance)
        if text_search:
            qs = qs.search(text_search)
        qs = qs.filter(**dict(attrquery(heads,query_from_string(filter))))\
               .exclude(**dict(attrquery(heads,query_from_string(exclude))))\
               .sort_by(order_by)
               
        max_display = max(int(max_display),1)
        items = qs[0:max_display]
        if not items:
            return display_if_empty
        if headers:
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

    
