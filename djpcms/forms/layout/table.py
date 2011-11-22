from djpcms import html
from djpcms.utils.text import nicename

from .base import FormWidget, FormLayoutElement


__all__ = ['TableFormElement','TableRow']


class TableRow(FormLayoutElement):
    
    def stream_errors(self, djp, children):
        for w in children:
            if isinstance(w,dict):
                yield '<td id="{0[error_id]}">{0[error]}</td>'.format(w)
            else:
                yield '<td></td>'
    
    def stream_fields(self, djp, children):
        for w in children:
            if isinstance(w,dict):
                if w['ischeckbox']:
                    yield '<td>{0[inner]}</td>'.format(w)
                else:
                    yield '<td><div class="{0[wrapper_class]}">\
{0[inner]}</div></td>'.format(w)
            else:
                yield '<td>{0}</td>'.format(w)
    
    def stream(self, djp, ctx):
        children = ctx['children']
        yield '<tr>'+''.join(self.stream_errors(djp, children))+'</tr>'
        yield '<tr>'+''.join(self.stream_fields(djp, children))+'</tr>'
        
    def get_context(self, djp, widget, keys):
        children = []
        for child in self.children_widgets(widget):
            if isinstance(child,FormWidget):
                ctx = child.get_context(djp)
            else:
                ctx = child.render(djp)
            children.append(ctx)
        return {'children': children}
        
    
class TableFormElement(FormLayoutElement):
    elem_css = "uniFormTable"
    tag = None
        
    def __init__(self, headers, *rows):
        self.headers = headers
        trows = []
        for row in rows:
            if not isinstance(row,TableRow):
                row = TableRow(*row)
            row.headers = headers
            trows.append(row)
        super(TableFormElement,self).__init__(*trows)

    def row_generator(self, djp, widget):
        for child in self.allchildren:
            if isinstance(child,TableRow):
                widget = self.child_widget(child, widget)
                for data in child.stream(djp,widget.get_context(djp)):
                    yield data
            
    def inner(self, djp, widget, keys):
        '''We override inner so that the actual rendering is delegate to
 :class:`djpcms.html.Table`.'''
        t1 = '<th>'
        t2 = '</th>'
        head = ''.join((t1+h+t2 for h in self.headers))
        rows = '\n'.join(self.row_generator(djp, widget))
        table = html.Widget('table',('<thead>',head,'</thead>',\
                                     '<tbody>',rows,'</tbody>'))\
                                    .addClass(self.elem_css)
        return table.render(djp)
    