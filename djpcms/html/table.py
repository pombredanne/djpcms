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
    '''A widget maker which render a dataTable.'''
    tag = 'div'
    default_class = 'data-table'
    table_media = Media(js = ['djpcms/datatables/jquery.dataTables.js',
                              'djpcms/datatables/TableTools/js/TableTools.min.js',
                              'djpcms/djptable.js'],
                        css = {'screen':['djpcms/datatables/TableTools/css/TableTools_JUI.css']})
    template = loader.template_class('''\
<table>
<thead>
 <tr>{% for head in headers %}
  <th>{{ head.sTitle }}</th>{% endfor %}
 </tr>
</thead>
<tbody>{% if rows %}{% for row in rows %}
<tr>{% for item in row %}
<td>{{ item }}</td>{% endfor %}
</tr>{% endfor %}{% endif %}
</tbody>{% if footer %}
<tfoot>
 <tr>{% for head in headers %}
  <th>{{ head.sTitle }}</th>{% endfor %}
 </tr>
</tfoot>{% endif %}
</table>
''')
    
    def get_context(self, djp, widget, key):
        ctx = {'headers':widget.data['options']['aoColumns'],
               'footer':widget.footer}
        appmodel = widget.internal['appmodel']
        toolbox = None
        if appmodel:
            toolbox = table_toolbox(appmodel,djp)
            widget.data.update(toolbox)
        if not widget.ajax:
            ctx['rows'] = widget.items(djp)
        return ctx
    
    def make_headers(self, headers):
        '''Generator of html headers tags'''
        for head in headers:
            w = Widget('th', cn = head.code)
            if head.description:
                w.addData('description',head.description)
            yield w.render(inner = head.name)
    
    def aoColumns(self, headers):
        '''Return an array of column definition to be used by the dataTable
javascript plugin'''
        for head in headers:
            yield {'bSortable':head.sortable,
                   'sClass':head.code,
                   'sName':head.code,
                   'sTitle':head.name,
                   'sWidth':head.width}
            
    def media(self):
        return self.table_media


class Table(Widget):
    '''Render a table given a response object ``djp``.

:parameter headers: iterable over headers. Must be provided.
:parameter body: optional iterable over data to display.
:parameter appmodel: optional application model instance.
:parameter model: optional model class.
:parameter nd: numeric accuracy for floating point numbers.
:parameter template_name: template name
    '''
    maker = TableMaker()
    size_choices = (10,25,50,100)
    
    def __init__(self, headers, body = None, appmodel = None,
                 model = None, paginator = None, toolbox = True,
                 ajax = None, size = 25, size_choices = None,
                 footer = True, **params):
        super(Table,self).__init__(**params)
        self.toolbox = toolbox
        self.ajax = ajax
        self.footer = footer
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
        
        options = {'aoColumns': list(self.maker.aoColumns(headers)),
                   'iDisplayLength ':size}
        if ajax or (paginator and paginator.multiple):
            options['bProcessing'] = False
            options['bServerSide'] = True
            if ajax:
                options['sAjaxSource'] = ajax
        self.addData('options',options)

    def items(self, djp):
        appmodel = self.internal['appmodel']
        headers = self.internal['headers']
        actions = None
        if appmodel:
            toolbox = table_toolbox(appmodel,djp)
            if 'actions' in toolbox:
                actions = toolbox.pop('actions')
            
        return (results_for_item(djp, headers, d,\
                appmodel, actions = actions) for d in self.internal['body'])
        