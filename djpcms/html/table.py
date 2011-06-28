'''\
Utilities for displaying interactive table with pagination and actions.
'''
from djpcms import http
from djpcms.template import loader

from .nicerepr import *
from .base import Widget, WidgetMaker
from .media import Media
from .apptools import table_toolbox, table_header

__all__ = ['Table']


class TableMaker(WidgetMaker):
    tag = 'div'
    default_class = 'data-table'
    table_media = Media(js = ['djpcms/datatables/jquery.dataTables.js',
                              'djpcms/datatables/TableTools/js/TableTools.min.js',
                              'djpcms/djptable.js'],
                        css = {'screen':['djpcms/datatables/TableTools/css/TableTools_JUI.css']})
    template = None
    template_name = ('datatable.html','djpcms/datatable.html')
    
    def get_context(self, djp, widget, key):
        appmodel = widget.internal['appmodel']
        headers = widget.internal['headers']
        paginator = widget.internal['paginator']
        body = widget.internal['body']
        toolbox = None
        actions = None
        if appmodel:
            toolbox = table_toolbox(appmodel,djp)
            if 'actions' in toolbox:
                actions = toolbox.pop('actions')
                widget.addData('actions',actions)
            
        items  = (results_for_item(djp, headers, d,\
                    appmodel, actions = actions) for d in body)
        return {'headers':list(self.make_headers(headers)),
                'items':items,
                'path': http.path_with_query(djp.request),
                'toolbox':toolbox}
    
    def make_headers(self, headers):
        '''Generator of html headers tags'''
        for head in headers:
            w = Widget('th', cn = head.code)
            if head.description:
                w.addData('description',head.description)
            yield w.render(inner = head.name)
            
    def media(self):
        return self.table_media


class Table(Widget):
    '''Render a table given a response object ``djp``.

:parameter headers: iterable over headers.
:parameter data: iterable over data to display.
:parameter model: optional model.
:parameter nd: numeric accuracy for floating point numbers.
:parameter template_name: template name
    '''
    maker = TableMaker()
    size_choices = (10,25,50,100)
    
    def __init__(self, headers, body = None, appmodel = None, model = None,
                 paginator = None, toolbox = True, ajax = None,
                 size = 25, size_choices = None, **params):
        super(Table,self).__init__(**params)
        self.toolbox = toolbox
        self.size_choices = size_choices or self.size_choices
        self.size = size
        self.paginator = paginator
        if appmodel and not model:
            model = appmodel.model
        if not model:
            try:
                model = body.model
            except AttributeError:
                pass
        headers = [table_header(head) for head in headers]
        super(Table,self).__init__(model = model,
                                   appmodel = appmodel,
                                   headers = headers,
                                   body = body,
                                   paginator = paginator,
                                   **params)
        
        options = {'aoColumns': [{'sName':head.code} for head in headers],
                   'iDisplayLength ':size}
        if ajax or (paginator and paginator.multiple):
            options['bProcessing'] = False
            options['bServerSide'] = True
            if ajax:
                options['sAjaxSource'] = ajax    
        self.addData('options',options)                     

