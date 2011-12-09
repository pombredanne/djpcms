from djpcms import html
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
                if w['ischeckbox']:
                    yield '<td>{0[inner]}</td>'.format(w)
                else:
                    yield '<td><div class="{0[wrapper_class]}">\
{0[inner]}</div></td>'.format(w)
            else:
                yield '<td>{0}</td>'.format(w)
    
    def stream(self, request, ctx):
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
        

class BaseTableFormElement(FormLayoutElement):

    def field_head(self, name, field):
        if field.is_hidden:
            return {'name':name}
        else:
            label = field.label or nicename(name)
            ch = html.Widget('span')
            if field.required:
                ch.addClass('required')
            return {'label': ch.render(inner = label),
                    'name':name,
                    'help_text':field.help_text}
            
    def row_generator(self, request, widget):
        for child in self.allchildren:
            if isinstance(child,TableRow):
                widget = self.child_widget(child, widget)
                for data in child.stream(request,widget.get_context(request)):
                    yield data
            
    def stream(self, request, widget, context):
        '''We override inner so that the actual rendering is delegate to
 :class:`djpcms.html.Table`.'''
        t1 = '<th>'
        t2 = '</th>'
        head = ''.join((t1+h+t2 for h in self.headers))
        rows = '\n'.join(self.row_generator(request, widget))
        table = html.Widget('table',('<thead>',head,'</thead>',\
                                     '<tbody>',rows,'</tbody>'))\
                                    .addClass(self.elem_css)
        yield table.render(request)
        
    
class TableFormElement(BaseTableFormElement):
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

