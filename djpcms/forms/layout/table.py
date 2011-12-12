from djpcms.html import Widget, table_header 
from djpcms.utils.text import nicename

from .base import FormWidget, FormLayoutElement


__all__ = ['TableFormElement','TableRow']


class TableRow(FormLayoutElement):
    '''A row in a form table layout'''
    def stream_errors(self, request, children):
        for w in children:
            if isinstance(w,dict):
                yield '<td id="{0[error_id]}">{0[error]}</td>'.format(w)
            else:
                yield '<td></td>'
    
    def stream_fields(self, request, children):
        for w in children:
            if isinstance(w,dict):
                w = w['widget'].render(request)
            yield '<td>{0}</td>'.format(w)
    
    def stream(self, request, widget, ctx):
        children = ctx['children']
        yield '<tr>'+''.join(self.stream_errors(request, children))+'</tr>'
        yield '<tr>'+''.join(self.stream_fields(request, children))+'</tr>'
        
    def get_context(self, request, widget, keys):
        children = []
        for child in self.children_widgets(widget):
            if isinstance(child,FormWidget):
                ctx = child.get_context(request)
            else:
                ctx = child.render(request)
            children.append(ctx)
        return {'children': children}
        

class TableFormElement(FormLayoutElement):
    elem_css = "uniFormTable"
    tag = None
        
    def __init__(self, headers, *rows, **kwargs):
        self.headers = list(self.field_heads(headers))
        self.fields = tuple(h.code for h in self.headers)
        trows = []
        for row in rows:
            if not isinstance(row,TableRow):
                row = TableRow(*row)
            trows.append(row)
        super(TableFormElement,self).__init__(*trows, **kwargs)

    def field_heads(self, headers):
        for name in headers:
            yield table_header(name)
            
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
                               cn = head.extraclass)\
                                .addClass('label')
                th.add(label)
                if head.description:
                    label.addData('content',head.description);
            yield th.render(request)
            
    def row_generator(self, request, widget, context):
        for child in self.allchildren:
            if isinstance(child,TableRow):
                w = self.child_widget(child, widget)
                yield w.render(request)
            
    def stream(self, request, widget, context):
        '''We override inner so that the actual rendering is delegate to
 :class:`djpcms.html.Table`.'''
        head = ''.join(self.render_heads(request, widget, context))
        rows = '\n'.join(self.row_generator(request, widget, context))
        table = Widget('table',('<thead>',head,'</thead>',\
                                 '<tbody>',rows,'</tbody>'))\
                                    .addClass(self.elem_css)
        yield table.render(request)
        
