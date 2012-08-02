from djpcms import forms, html, views, media
from djpcms.cms import permissions
from djpcms.forms import layout as uni
from djpcms.html import classes
from djpcms.utils import orms
from djpcms.utils.text import to_string
from djpcms.utils.httpurl import QueryDict
from djpcms.cms.plugins import DJPplugin

class ModelChoice(forms.ChoiceFieldOptions):

    def _query(self, bfield):
        '''Generator of model Choices'''
        form = bfield.form
        request = form.request
        if request:
            root = form.request.view.root
            models = set()
            for app in root.applications():
                mapper = app.mapper
                if mapper and app.model not in models:
                    models.add(app.model)
                    req = request.for_app(app)
                    if req.has_permission(permissions.ADD):
                        yield mapper.hash, str(mapper), req

    def query(self, bfield):
        for id, text, req in sorted(self._query(bfield), key=lambda y : y[1]):
            yield html.Widget('option', text, value=id, data={'href': req.url})


class FieldChoices(forms.ChoiceFieldOptions):

    def _query(self, bfield):
        form = bfield.form
        request = form.request
        model = form.data.get('for_model')
        if request and model:
            app = request.app_for_model(model)
            if app and app.pagination:
                for head in app.pagination.list_display:
                    yield head.code, head.name

    def query(self, bfield):
        return sorted(self._query(bfield), key=lambda y : y[1])


def get_contet_choices(bfield):
    model = bfield.form.model
    if not model:
        return []
    else:
        request = bfield.form.request
        if request:
            request = request.for_model(model)
            if request:
                return request.view.query(request)
        return orms.mapper(model).query()

def header_query(bfield):
    form = bfield.form
    data = form.request.POST
    return ()


class ForModelForm(forms.Form):
    for_model = forms.ChoiceField(
                    required=False,
                    choices=ModelChoice(empty_label='Select a model'),
                    widget=html.Select(cn=classes.model))

    def clean_for_model(self, mhash):
        if mhash:
            try:
                return self.request.view.root.for_hash(mhash,safe=False)
            except Exception as e:
                raise forms.ValidationError(str(e))


class ModelItemListForm(ForModelForm):
    max_display = forms.IntegerField(initial=10,
                                     widget=html.TextInput(cn='span1'))
    text_search = forms.CharField(required=False)
    filter = forms.CharField(required=False)
    exclude = forms.CharField(required=False)
    order_by = forms.ChoiceField(required=False,
                                 widget=html.Select(cn='model-fields'),
                                 choices=FieldChoices())
    descending = forms.BooleanField(initial=False)
    headers = forms.ChoiceField(required=False,
                                widget=html.Select(cn='model-fields'),
                                choices=FieldChoices(multiple=True))
    table_footer = forms.BooleanField(initial=False, label='footer')
    display_if_empty = forms.BooleanField(initial=False)

HtmlModelListForm = forms.HtmlForm(
    ModelItemListForm,
    layout=uni.FormLayout(
                uni.Fieldset('for_model', 'text_search', 'filter', 'exclude'),
                uni.Inlineset('order_by', 'descending', label='Ordering'),
                uni.Inlineset('max_display', 'display_if_empty', 'table_footer',
                              label='Max display'),
                uni.Fieldset('headers'),
                tag='div',
                cn='model-filters'),
)


class FormModelForm(ForModelForm):
    method      = forms.ChoiceField(choices=(('get','get'),('post','post')),
                                    initial='get')
    ajax        = forms.BooleanField(initial=False)


class ModelLinksForm(forms.Form):
    size = forms.ChoiceField(choices=(('', 'standard'),
                                      (classes.button_large, 'large'),
                                      (classes.button_small, 'small')),
                             required=False)
    for_instance = forms.BooleanField()
    layout = forms.ChoiceField(choices=(('group left','group left'),
                                        ('group right','group right'),
                                        ('horizontal','horizontal'),
                                        ('vertical','vertical')))
    for_instance = forms.BooleanField()
    exclude = forms.CharField(max_length=600, required=False)
    include = forms.CharField(max_length=600, required=False)


class ContentForm(forms.Form):
    content = forms.ChoiceField(choices=forms.ChoiceFieldOptions(\
                                    query=get_contet_choices))
#TODO, MAKE THIS AUTOCOMPLETE IF POSSIBLE
                                    #autocomplete = True))
#
#______________________________________________ PLUGINS

class RenderObject(DJPplugin):
    '''Render an instance of a model using the
:attr:`Application.instance_view`.'''
    virtual = True
    form = ContentForm
    view = 'view'
    def get_object(self, request, content):
        model = self.for_model(request)
        if content and model:
            return orms.mapper(model).get(id=content)

    def render(self, request, block, prefix, content=None, **kwargs):
        instance = self.get_object(request, content)
        if instance:
            request = request.for_model(instance=instance, name=self.view)
            if request:
                return request.render(block=block)
            else:
                return to_string(instance)
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

    def render(self, request, wrapper, prefix, layout='group',
               size='', exclude='', include='',
               for_instance=False, **kwargs):
        appmodel = request.view.appmodel
        if not appmodel:
            return
        exclude = None if not exclude else exclude.split(',')
        include = None if not include else include.split(',')
        instance = None if not for_instance else request.instance
        links = views.application_links(
                            views.application_views(request,
                                                    exclude=exclude,
                                                    include=include,
                                                    instance=instance),
                            asbuttons=True)
        if appmodel.mapper:
            name = appmodel.mapper.class_name(appmodel.model)
        else:
            name = None
        if links:
            links = [link[1].addClass(size) for link in links]
            if layout.startswith('group'):
                d = html.Widget('div', links, cn=classes.button_group)
                if layout == 'group right':
                    d.addClass(classes.float_right)
                return d
            else:
                return html.Widget('ul', (l[1] for l in links), cn = name)\
                           .addClass('model-links')\
                           .addClass(layout)\
                           .render(request)


def attrquery(heads, query):
    for k, v in query.lists():
        if k in heads:
            k = heads[k].attrname
        yield k, v


class ModelItemsList(DJPplugin):
    '''Filter a model according to editable criteria snd displays a
certain number of items as specified in the max display input.'''
    name = 'model-items'
    description = 'Filtered items for a model'
    form = HtmlModelListForm

    def ajax__for_model(self, request, for_model):
        pass

    def render(self, request, block, prefix, for_model=None, max_display=5,
               filter=None, exclude=None, order_by =None, descending=False,
               text_search=None, headers=None, display_if_empty='',
               table_footer=False, **kwargs):
        instance = request.instance
        request = request.for_model(for_model)
        if request is None or request.model is None:
            return ''
        view = request.view
        appmodel = view.appmodel
        mapper = appmodel.mapper
        load_only = ()
        thead = None
        appheads = request.pagination.headers

        if headers:
            thead = []
            for head in headers:
                if head in appheads:
                    thead.append(appheads[head])

        # Ordering
        if order_by:
            order_by = html.attrname_from_header(appheads, order_by)
            if order_by and descending:
                order_by = '-{0}'.format(order_by)

        # query with the instancde of the current page
        qs = view.query(request, instance=instance)
        if text_search:
            qs = qs.search(text_search)
        filter = mapper.query_from_mapping(
                                attrquery(appheads, QueryDict(filter)))
        exclude = mapper.query_from_mapping(
                                attrquery(appheads, QueryDict(exclude)))
        qs = qs.filter(**filter).exclude(**exclude).sort_by(order_by)\
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
            render_instance = appmodel.render_instance_list
            w.add((render_instance(request, item) for item in items))
            return w


