'''\
Utilities for displaying interactive table with pagination and actions.

It uses the Datatable jQuery plugin on the client side.

http://www.datatables.net/
'''
from functools import partial
from copy import deepcopy
from collections import namedtuple

from djpcms.utils import media
from djpcms.utils.ajax import simplelem
from djpcms.utils.text import nicename
from djpcms.utils.const import EMPTY_VALUE

from .nicerepr import *
from .base import Widget, WidgetMaker
from .pagination import Paginator 


__all__ = ['TableMaker',
           'Pagination',
           'table_header',
           'attrname_from_header',
           'simple_table_dom']


table_header_ = namedtuple('table_header_',
'code name description function sortable width extraclass attrname')

simple_table_dom = {'sDom':'t'}


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
    if not name:
        if code == '__str__':
            name = EMPTY_VALUE
        else:
            name = nicename(code)
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
        ctx = widget.internal.copy()
        pagination = ctx.pop('pagination',None)
        options = widget.data.get('options')
        if options is None:
            options = {}
            widget.data['options'] = options
        if pagination:
            options.update({'bPaginate': True,
                            'iDisplayLength': pagination['per_page'],
                            'aLengthMenu':pagination['page_menu']})
        else:
            options['bPaginate'] = False
        headers = list(self.aoColumns(ctx['headers']))
        widget.data['options']['aoColumns'] = headers
        ctx.update({'headers': headers, 'title':title})
        ctx['rows'] = self.stream(djp, widget, ctx)
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
    
    def stream(self, djp, widget, context = None):
        if widget.data_stream:
            headers = widget.internal['headers']
            appmodel = widget.internal.get('appmodel')
            actions = widget.internal.get('actions')                
            return (results_for_item(djp, headers, res, appmodel,
                            actions = actions) for res in widget.data_stream)
        else:
            return ()
        

_TableMaker = TableMaker()


def table(headers, body, **kwargs):
    return Widget(_TableMaker,body,headers=headers,**kwargs)


class Pagination(object):
    '''Class for specifying options for a table or a general pagination.
    
:parameter headers: Optional iterable of headers. If specified the pagination
    will be rendered as a :class:`Table`.

:parameter size: The number of elements to display in one page.
    If set to ``None``, all elements will be displayed.

    Default: ``25``.

:parameter size_choices: A list or tuple of size choices.

    Default: ``(10,25,50,100)``.
    
:parameter actions: a list of actions available to the table.

    Default: ``[]``
:parameter bulk_actions: a list of bulk actions available to the table.

    Default: ``[]``
    
:parameter sortable: default value for the headers sortable attribute.

    Default: ``False``
    
:parameter ordering: ptional string indicating the default field for ordering.
    Starting with a minus means in descending order.
    
        Default ``None``
    
:parameter footer: when ``True`` the table will display the footer element.

    Default: ``False``.
    
:parameter ajax: enable ``ajax`` interaction.

    Default: ``True``.
    
:parameter html_data: dictionary of data to add to the pagination
    :class:`Widget`
    
    Default: None
'''
    default_pagination_template_name = ('pagination.html',
                                        'djpcms/pagination.html')
    table_defaults = {
          'bJQueryUI':True,
          'sPaginationType': 'full_numbers',
          'sDom': '<"H"<"row-selector"><"col-selector">T<"clear">ilrp>t<"F"ip>'}
    flat_defaults = {}
    
    def __init__(self, headers = None, actions = None, bulk_actions = None,
                 sortable = False, footer = False, ajax = True,
                 size = 25, size_choices = (10,25,50,100), ordering = None,
                 html_data = None, sizetolerance = 1,
                 pagination_template_name = None, widget_factory = None):
        self.actions = tuple(actions or ())
        self.bulk_actions = tuple(bulk_actions or ())
        self.footer = footer
        self.size = size
        self.size_choices = size_choices
        self.ordering = ordering
        self.sizetolerance = sizetolerance
        self.ajax = ajax
        self.widget_factory = widget_factory
        template_name = pagination_template_name or \
                        self.default_pagination_template_name
        self.widget_maker = WidgetMaker(template_name = template_name)
        heads = {}
        ld = []
        if headers:
            for head in headers:
                head = table_header(head, sortable = sortable)
                heads[head.code] = head
                ld.append(head)
        self.list_display = tuple(ld)
        self.headers = heads
        self.html_data = html_data or {}
        
    @property
    def astable(self):
        return bool(self.headers)
    
    def defaultdata(self):
        if self.astable:
            return deepcopy(self.table_defaults)
        else:
            return deepcopy(self.flat_defaults)
    
    def paginate(self, data, start = 0, per_page = None, withbody = True):
        '''paginate *data* according to :attr:`size` and return a two elements
tuple containing the pagination dictionary and the (possibly) reduced data.

:parameter data: queryset or list of data
:parameter start: start point
:parameter per_page: number of element per page
:parameter withbody: if ``False`` the data set won't be reduced.
:rtype: two elements tuple
'''
        per_page = per_page or self.size
        if not per_page:
            return self._paginate(None,data,withbody)
        try:
            total = data.count()
        except:
            total = len(data)
        per_page = int(per_page)
        if per_page <= 0:
            return self._paginate(None,data,withbody)
        if total <= self.sizetolerance*per_page:
            return self._paginate(None,data,withbody)
        tp = int(total/per_page)
        if per_page*tp < total:
            tp += 1
        pages = tp
        multiple = pages > 1
        start = int(start)
        page = int(start/per_page)
        if page*per_page <= start:
            page += 1
        end = page*per_page
        start = end - per_page
        end = min(end,total)
        page_menu = self.size_choices if multiple else None
        pagi = {'total':total,
                'per_page':per_page,
                'pages':pages,
                'page':page,
                'multiple':multiple,
                'start':start,
                'end':end,
                'page_menu':page_menu}
        return self._paginate(pagi,data,withbody)
        
    def _paginate(self,pagi,data,withbody):
        if withbody:
            if pagi:
                return pagi,data[pagi['start']:pagi['end']]
            else:
                return pagi,list(data)
        else:
            return pagi,None

    def widget(self, body, toolbox = None, pagination = None, ajax = None,
               **kwargs):
        '''Return the pagination widget. This is either a *table* or
 a standard pagination.
 
:parameter body: body to paginate. An iterable over data.
:parameter toolbox: Additional tool to display in the pagination page.
:parameter pagination: disctionary containing pagination information.
'''
        data = self.defaultdata()
        data.update(deepcopy(self.html_data))
        if toolbox:
            data.update(toolbox)
        if 'options' not in data:
            options = {}
            data['options'] = options
        
        options = data['options']
        
        if self.astable:
            if ajax:
                options['bProcessing'] = True
                options['bServerSide'] = True
                if ajax:
                    options['sAjaxSource'] = ajax
            maker = partial(table, self.list_display)
        elif self.widget_factory:
            maker = self.widget_factory
        else:
            raise NotImplementedError
        return maker(body, pagination = pagination, data = data,
                     footer = self.footer, **kwargs)
        
    def ajaxresponse(self, djp, body, **kwargs):
        widget = self.widget(body, **kwargs)
        pagination = widget.internal.get('pagination')
        if self.astable:
            aaData = []
            for item in widget.maker.stream(djp,widget):
                id = item['id']
                aData = {} if not id else {'DT_RowId':id}
                aData.update(((i,v) for i,v in enumerate(item['display'])))
                aaData.append(aData)
            if pagination:
                total = pagination['total']
            else:
                total = len(aaData)
            inputs = djp.request.REQUEST
            data = {'iTotalRecords':total,
                    'iTotalDisplayRecords':total,
                    'sEcho':inputs.get('sEcho'),
                    'aaData':aaData}
            return simplelem(data)
        else:
            raise NotImplementedError()
        
        
    def default_paginator(self, body, pagination = None, data = None,
                          footer = False):
        c  = djp.kwargs.copy()
        c.update({'paginator': p,
                  'djp': djp,
                  'url': djp.url,
                  'appmodel': self,
                  'headers': self.headers})
        maker = self.object_widgets['pagination']
        render = self.render_object
        qs = query[p.start:p.end]
        c['items'] = (render(djp,item,'pagination') for item in qs)
        return djp.render_template(self.pagination_template_name, c)