from djpcms import html
from djpcms.utils.text import nicename

from .base import FormWidget, FormLayoutElement


__all__ = ['TableFormElement','TableRow']


class TableRow(FormLayoutElement):
    
    def stream_errors(self, djp, children):
        for w in children:
            if isinstance(w,dict):
                yield ''
            else:
                yield ''
    
    def stream_fields(self, djp, children):
        for w in children:
            if isinstance(w,dict):
                yield w['inner']
            else:
                yield w
    
    def stream(self, djp, ctx):
        children = ctx['children']
        yield self.stream_errors(djp, children)
        yield self.stream_fields(djp, children)
        
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
        table = html.Table(self.headers,
                           self.row_generator(djp, widget),
                           data = {'options':{'sDom':'t'}},
                           footer = False).addClass(self.elem_css)
        return table.render(djp)
    