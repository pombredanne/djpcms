from djpcms.html import Widget, WidgetMaker, table_header 
from djpcms.utils.text import nicename

from .base import FormWidget, FieldTemplate, FormLayoutElement


__all__ = ['TableFormElement','TableRow']


class TableRow(FormLayoutElement):
    '''A row in a table rendering a form.'''
    field_widget_tag = 'td'
    field_widget_class = None
    
    def stream_errors(self, request, children):
        '''Create the error ``td`` elements.
They all have the class ``error``.'''
        for w in children:
            b = w.bfield
            if b:
                yield '<td id="%s" class="error">%s</td>'%(b.errors_id,b.error)
            else:
                yield '<td class="error"></td>'
    
    def stream_fields(self, request, children):
        for w in children:
            b = w.bfield
            if not b:
                w = Widget('td', w.maker.key).addClass('one-line')
            elif b.widget.attrs.get('type') == 'checkbox':
                w.addClass('checkbox')
            yield w.render(request)
    
    def stream(self, request, widget, context):
        '''We override stream since we don't care about a legend in a
table row'''
        children = list(widget.allchildren())
        yield '<tr class="error-row">'+\
                ''.join(self.stream_errors(request, children))+'</tr>'
        yield '<tr>'+''.join(self.stream_fields(request, children))+'</tr>'
        

class TableFormElement(FormLayoutElement):
    '''A :class:`FormLayoutElement` for rendering a group of :class:`Field`
in a table.

:parameter headers: The headers to display in the table.
'''
    tag = 'div'
    default_style = 'tablefield'
    elem_css = "uniFormTable"
        
    def __init__(self, headers, *rows, **kwargs):
        # each row must have the same number of columns as the number of headers
        self.headers = [table_header(name) for name in headers]
        self.fields = tuple(h.code for h in self.headers)
        trows = []
        for row in rows:
            if not isinstance(row,TableRow):
                row = TableRow(*row)
            trows.append(row)
        super(TableFormElement,self).__init__(*trows, **kwargs)

    def render_heads(self, request, widget, context):
        '''Generator of rendered table heads'''
        for head in self.headers:
            name = head.code
            th = Widget('th', cn = name)
            if head.hidden:
                th.addClass('djph')
            else:
                label = Widget('span', head.name,
                               title = head.name,
                               cn = head.extraclass).addClass('label')
                th.add(label)
                if head.description:
                    label.addData('content',head.description);
            yield th.render(request)
            
    def row_generator(self, request, widget, context):
        for row in widget.allchildren():
            yield row.render(request)
            
    def stream(self, request, widget, context):
        '''We override inner so that the actual rendering is delegate to
 :class:`djpcms.html.Table`.'''
        rows = list(self.row_generator(request, widget, context))
        if rows:
            head = ''.join(self.render_heads(request, widget, context))
            body = Widget('body', rows)
            table = Widget('table',('<thead><tr>',head,'</tr></thead>',body))
            yield table.addClass(self.elem_css).render(request)
        
