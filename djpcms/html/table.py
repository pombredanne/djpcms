'''\
Utilities for displaying interactive table with pagination and actions.
'''
from djpcms import http
from djpcms.template import loader

from .nicerepr import *
from .base import HtmlWidget
from .media import Media
from .apptools import table_toolbox, table_header

__all__ = ['Table']


class Table(object):
    table_media = Media(js = ['djpcms/jquery.dataTables.min.js'])
    template_name = ('tablesorter.html',
                     'djpcms/tablesorter.html')
    
    def __init__(self,
                 djp,
                 headers = None,
                 data = None,
                 model = None,
                 template_name = None,
                 paginator = None,
                 appmodel = None,
                 nice_headers_handler = None,
                 nd = 3):
        '''\
Render a table given a response object ``djp``.

:parameter djp: instance of :class:`djpcms.views.DjpResponse`.
:parameter headers: iterable over headers.
:parameter data: iterable over data to display.
:parameter model: optional model.
:parameter nd: numeric accuracy for floating point numbers.
:parameter template_name: template name
    '''
        self.template_name = template_name or self.template_name
        if not model:
            # try to get model from data
            try:
                model = data.model
            except AttributeError:
                pass
        path  = http.path_with_query(djp.request)
        
        # model available
        if model:
            mapper = djp.mapper(model)
            appmodel = djp.view.site.for_model(model)
        else:
            #appmodel = appmodel or djp.view.appmodel
            if appmodel:
                mapper = appmodel.mapper
            else:
                mapper = None
        
        toolbox = None
        actions = False
        if appmodel:
            toolbox = table_toolbox(appmodel,djp)
            actions = 'actions' in toolbox
            
        items  = (results_for_item(djp, headers, d, appmodel,\
                                   mapper = mapper,\
                                   actions = actions,\
                                   nd = nd, path = path) for d in data)
        
        nice_headers_handler = nice_headers_handler or nice_headers 
        self.ctx = {'headers': list(self.headers(headers)),
                    'items': items,
                    'toolbox':toolbox,
                    'paginator':paginator,
                    'options':''}
        options = {}
        if paginator and paginator.multiple:
            options['clientSort'] = False
        
        if options:
            w = HtmlWidget().addData('options',options)
            self.ctx['options'] = w.flatatt() 
            
    def headers(self, headers):
        '''Generator of hteml headers tags'''
        for head in headers:
            head = table_header(head)
            w = HtmlWidget('th', cn = head.code)
            if head.description:
                w.addData('description',head.description)
            yield w.render(inner = head.name)
            
    def render(self):
        return loader.render(self.template_name,self.ctx)

    def media(self):
        return self.table_media


