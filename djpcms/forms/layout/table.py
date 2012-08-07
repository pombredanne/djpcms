from djpcms import media
from djpcms.html import Widget, WidgetMaker, table_header
from djpcms.utils.text import nicename

from .base import FormWidget, FieldTemplate, FormLayoutElement, classes


__all__ = ['TableRow', 'TableFormElement', 'TableRelatedFieldset']


class BaseTable(FormLayoutElement):
    show_field_labels = False
    field_widget_class = None

    def field_widget(self, widget):
        # Override field_widget so that the container for errors is not added
        return Widget('div', widget.bfield.widget)


class TableRow(BaseTable):
    '''A row in a table rendering a group of :class:`Fields`.'''
    field_widget_tag = 'td'

    def stream_errors(self, request, children):
        '''Create the error ``td`` elements.
They all have the class ``error``.'''
        for w in children:
            b = w.bfield
            w = Widget('td', cn='error')
            if b:
                w.addClass(b.widget.attrs.get('type'))\
                 .add(b.error).addAttr('id', b.errors_id)
            yield w

    def stream_fields(self, request, children):
        for w in children:
            b = w.bfield
            if not b:
                w.addClass(w.field)
            else:
                w.addClass(b.widget.attrs.get('type'))
            yield w.render(request)

    def stream(self, request, widget, context):
        '''We override stream since we don't care about a legend in a
table row'''
        children = list(widget.allchildren())
        yield Widget('tr', self.stream_errors(request, children))\
                    .addClass('error-row')
        yield Widget('tr', self.stream_fields(request, children))


class BaseTableElement(BaseTable):
    '''A :class:`FormLayoutElement` for rendering a group of :class:`Field`
in a table.

:parameter headers: The headers to display in the table.
'''
    tag = 'div'
    elem_css = "uniFormTable"
    _media = media.Media(js=['djpcms/plugins/delete_row.js'])

    def __init__(self, headers, *children, **kwargs):
        # each row must have the same number of columns as the number of headers
        self.headers = [table_header(name) for name in headers]
        self.fields = tuple(h.code for h in self.headers)
        super(BaseTableElement, self).__init__(*children, **kwargs)

    def render_heads(self, request, widget, context):
        '''Generator of rendered table heads'''
        for head in self.headers:
            name = head.code
            th = Widget('th', head.name, cn=name, title=head.description)\
                        .addClass(head.extraclass)
            yield th.render(request)

    def rows(self, widget):
        raise NotImplementedError()

    def row_generator(self, request, widget, context):
        for row in self.rows(widget):
            for tr in row.stream(request, context):
                yield tr

    def stream(self, request, widget, context):
        '''We override inner so that the actual rendering is delegate to
 :class:`djpcms.html.Table`.'''
        for s in super(BaseTableElement, self).stream(request, widget, context):
            yield s
        tr = Widget('tr', self.render_heads(request, widget, context))
        head = Widget('thead', tr)
        body = Widget('tbody', self.row_generator(request, widget, context))
        table = Widget('table', (head, body))
        yield table.addClass(self.elem_css).render(request)


class TableFormElement(BaseTableElement):

    def __init__(self, headers, *rows, **kwargs):
        # each row must have the same number of columns as the number of headers
        trows = []
        for row in rows:
            if not isinstance(row, TableRow):
                row = TableRow(*row)
            trows.append(row)
        super(TableFormElement,self).__init__(headers, *trows, **kwargs)

    def rows(self, widget):
        return widget._rows

    def stream(self, request, widget, context):
        widget._rows = []
        children = widget.children.__class__()
        for row in widget.allchildren():
            if isinstance(row.maker, TableRow):
                widget._rows.append(row)
            else:
                children[row.key] = row
        widget.children = children
        return super(TableFormElement, self).stream(request, widget, context)


class TableRelatedFieldset(BaseTableElement):
    '''A :class:`djpcms.forms.layout.TableFormElement`
class for handling related :class:`djpcms.forms.FieldSet`.'''

    def __init__(self, form, formset, fields=None, delete_head='', **kwargs):
        self.formset = formset
        self.form_class = form.base_inlines[formset].form_class
        self.delete_head = delete_head
        headers = list(self.get_heads(fields))
        super(TableRelatedFieldset,self).__init__(headers, **kwargs)
        self.row_maker = TableRow(*self.fields)
        self.row_maker.check_fields(list(self.fields))

    def get_heads(self, fields):
        headers = list(fields or ())
        dfields = self.form_class.base_fields
        self.hidden_fields = []
        for field in dfields:
            if field not in headers:
                headers.append(field)
        for name in headers:
            field = dfields.get(name)
            if field:
                label = field.label or nicename(name)
                cn = ('required' if field.required else None,
                      field.widget.attr('type'))
                help_text = field.help_text
            else:
                label = nicename(name)
                help_text = None
                cn=None
            yield table_header(name, label, help_text, extraclass=cn)
        if self.delete_head is not None:
            yield table_header(classes.delete_row, self.delete_head)

    def rows(self, widget):
        formset = widget.form.form_sets[self.formset]
        for form in formset.forms:
            yield self.child_widget(self.row_maker, widget, form=form)

    def stream(self, request, widget, context):
        for data in super(TableRelatedFieldset, self).stream(request,\
                                                             widget, context):
            yield data
        formset = widget.form.form_sets[self.formset]
        # Loop over hidden fields
        if self.hidden_fields:
            for form in formset.forms:
                for field in self.hidden_fields:
                     child = self.child_widget(field, widget, form=form)
                     yield child.render(request)
        # the number of forms
        yield formset.num_forms(cn=classes.number_of_forms).render(request)

