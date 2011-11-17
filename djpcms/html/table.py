'''\
Utilities for displaying interactive table with pagination and actions.

It uses the Datatable jQuery plugin on the client side.

http://www.datatables.net/
'''
from collections import namedtuple

from djpcms.utils import media
from djpcms.utils import ajax
from djpcms.utils.text import nicename

from .nicerepr import *
from .base import Widget, WidgetMaker
from .pagination import Paginator 


__all__ = ['Table','table_header','attrname_from_header']


table_header_ = namedtuple('table_header_',
'code name description function sortable width extraclass attrname')


def attrname_from_header(header, code):
    if code and code in header:
        return header[code].attrname
    return code


def table_header(code, name = None, description = None, function = None,
                 attrname = None, sortable = True, width = None,
                 extraclass = None):
    '''Utility for creating an instance of a :class:`table_header_` namedtuple.
    
:param code: unique code for the header
:param attrname: optional attribute name, if not supplied the *code* will be
    used. The attrname is the actual attribute name in the object, and
    therefore the actual field in the database. 
'''
    if isinstance(code,table_header_):
        return code
    name = name or nicename(code)
    function = function or code
    attrname = attrname or code
    return table_header_(code,name,description,function,sortable,width,
                         extraclass,attrname)

class TableMaker(WidgetMaker):
    '''A widget maker which render a dataTable.'''
    tag = 'div'
    default_class = 'data-table'
    table_media = media.Media(
            js = [
                  'djpcms/datatables/jquery.dataTables.js',
                  'djpcms/datatables/ColVis/js/ColVis.js',
                  'djpcms/datatables/TableTools/js/TableTools.min.js',
                  'djpcms/djptable.js'],
            css = {'screen':
                    ['djpcms/datatables/TableTools/css/TableTools_JUI.css']
                    }
        )
    template = '''{% if title %}
<h3 class='table-title ui-widget-header'>{{ title }}</h3>{% endif %}
<table>
<thead>
 <tr>{% for head in headers %}{% if head.description %}
  <th class="hint" title="{{ head.description }}">{% else %}
  <th>{% endif %}{{ head.sTitle }}</th>{% endfor %}
 </tr>
</thead>
<tbody>{% if rows %}{% for row in rows %}
<tr{% if row.id %} class="{{ row.id }}"{% endif %}>{% for item in row.display %}
<td>{{ item }}</td>{% endfor %}
</tr>{% endfor %}{% endif %}
</tbody>{% if footer %}
<tfoot>
 <tr>{% for head in headers %}
  <th>{{ head.sTitle }}</th>{% endfor %}
 </tr>
</tfoot>{% endif %}
</table>
'''
    
    def get_context(self, djp, widget, key):
        title = widget.attrs.get('title')
        ctx = {'headers':widget.data['options']['aoColumns'],
               'footer':widget.footer,
               'title':title}
        appmodel = widget.internal['appmodel']
        toolbox = widget.toolbox
        if toolbox:
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
            cn = [head.code]
            if head.extraclass:
                cn.append(head.extraclass)
            so = head.sortable
            if so:
                cn.append('sortable')
            yield {'bSortable':head.sortable,
                   'sClass':' '.join(cn),
                   'sName':head.code,
                   'sTitle':head.name,
                   'sWidth':head.width,
                   'description':head.description}
            
    def media(self, djp = None):
        return self.table_media


class Table(Widget):
    '''A Table :class:`djpcms.html.Widget` packed with functionalities
and rendered using the dataTable_ jQuery plugin.

:parameter headers: iterable over headers. Must be provided.
:parameter body: optional iterable over data to display.
:parameter appmodel: optional :class:`djpcms.views.Application` instance.
:parameter model: optional model class. If not provided the model in appmodel
    will be used.
:parameter toolbox: optional dictionary with table toolbox data. Created using
    the :func:`djpcms.html.table_toolbox` function.
:parameter footer: flag indicating if a table footer is required.

    Default ``False``.

.. _dataTable: http://www.datatables.net/
    '''
    maker = TableMaker()
    size_choices = (10,25,50,100)
    
    def __init__(self, headers, body = None, appmodel = None,
                 model = None, paginator = None, toolbox = None,
                 ajax = None, size = 25, size_choices = None,
                 paginate = True, footer = False, title = None,
                 **params):
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
                   'iDisplayLength':size,
                   'bPaginate':paginate}
        if ajax or (paginator and paginator.multiple):
            options['bProcessing'] = True
            options['bServerSide'] = True
            if ajax:
                options['sAjaxSource'] = ajax
        if 'options' in self.data:
            options.update(self.data['options'])
        self.addData('options',options).addAttr('title',title)

    def items(self, djp):
        body = self.internal['body']
        if body:
            appmodel = self.internal['appmodel']
            headers = self.internal['headers']
            actions = None
            if appmodel and self.toolbox:
                if 'actions' in self.toolbox:
                    actions = self.toolbox.pop('actions')
                
            return (results_for_item(djp, headers, d, appmodel,
                                     actions = actions) for d in body)
        else:
            return ()
        

