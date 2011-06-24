'''\
Utilities for displaying interactive table with pagination and actions.
'''
from djpcms import http
from djpcms.template import loader

from .nicerepr import *
from .base import Widget,WidgetMaker
from .media import Media
from .apptools import table_toolbox, table_header

__all__ = ['Table']


class TableMaker(WidgetMaker):
    tag = 'table'
    default_class = 'dataTable'
    table_media = Media(js = ['djpcms/jquery.dataTables.min.js'])
    template_name = ('tablesorter.html',
                     'djpcms/tablesorter.html')
    
    
    def media(self):
        return self.table_media
    
    
DataTableMaker = WidgetMaker(
    template_name = ('datatable.html','djpcms/datatable.html'),
    default = 'datatable',
    ).add(TableMaker())
    

class Table(Widget):
    '''Render a table given a response object ``djp``.

:parameter headers: iterable over headers.
:parameter data: iterable over data to display.
:parameter model: optional model.
:parameter nd: numeric accuracy for floating point numbers.
:parameter template_name: template name
    '''
    maker = DataTableMaker
    
    def __init__(self, headers, body, appmodel = None, model = None,
                 paginator = None, toolbox = True, **params):
        super(Table,self).__init__(**params)
        self.toolbox = True
        self.paginator = paginator
        if appmodel and not model:
            model = appmodel.model
        if not model:
            try:
                model = body.model
            except AttributeError:
                pass
        if model:
            appmodel = djp.view.site.for_model(model)
        self.model = model
        self.appmodel = appmodel
        self.headers = [table_header(head) for head in headers]
        self.body = body
        self.addData('options',{})
        if paginator and paginator.multiple:
            self.data['options']['serverside'] = True
            
    def make_headers(self, headers):
        '''Generator of hteml headers tags'''
        for head in headers:
            w = Widget('th', cn = head.code)
            if head.description:
                w.addData('description',head.description)
            yield w.render(inner = head.name)
        
    def get_context(self, djp, context, *args, **kwargs):
        appmodel = self.appmodel
        actions = None
        if appmodel:
            toolbox = table_toolbox(appmodel,djp)
            actions = 'actions' in toolbox
        items  = (results_for_item(djp, headers, d,\
                    appmodel, actions = actions) for d in self.body)
        context.update({'headers':list(self.make_headers(headers)),
                        'data':items,
                        'model':self.model,
                        'appmodel':appmodel})
        path  = http.path_with_query(djp.request)
        return loader.render(self.template_name,self.ctx)

