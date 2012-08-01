from djpcms import html, forms, views
from djpcms.html import classes
from djpcms.forms import layout as uni


def search_form(name='SearchForm', placeholder='search', input_name=None,
                submit=None, cn=None, choices=None, label='search text',
                deafult_style=uni.nolabel, on_submit=None,
                required=False, **kwargs):
    '''Create a new :class:`djpcms.forms.HtmlForm` for searching.

:parameter name: name of the :class:`Form`
:parameter placeholder: text for the ``placeholder`` input attribute.
:parameter submit: submit text. If not provided, the form will submit on enter
    key-stroke.
:parameter cn: additional class names for the input element in the form.
'''
    submit = submit or ()
    input_name = input_name or forms.SEARCH_STRING
    widget = html.TextInput(placeholder=placeholder, cn=cn)
    if not submit:
        widget.addData('options', {'submit': True})
        layout = uni.FormLayout(default_style=deafult_style)
    else:
        submit = ((submit,'search'),)
        layout = uni.FormLayout(uni.Inlineset(input_name, uni.SUBMITS),
                                default_style=deafult_style)
    if choices:
        field = forms.ChoiceField(attrname=input_name,
                                  label=label,
                                  required=required,
                                  choices=choices,
                                  widget=widget)
    else:
        field = forms.CharField(attrname=input_name,
                                label=label,
                                required=required,
                                widget=widget)
    form_cls = forms.MakeForm(name, (field,), on_submit=on_submit)

    return forms.HtmlForm(form_cls,
                          inputs=submit,
                          layout=layout,
                          **kwargs)