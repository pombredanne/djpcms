from djpcms import html, forms, views
from djpcms.html import classes
from djpcms.forms import layout


def search_form(name='SearchForm', placeholder='search', input_name=None,
                submit=None, cn=None, choices=None,
                deafult_style=layout.nolabel, **kwargs):
    '''Create a new :class:`djpcms.forms.HtmlForm` for searching.
    
:parameter name: name of the :class:`Form`
'''
    submit = submit or ()
    input_name = input_name or forms.SEARCH_STRING
    widget = html.TextInput(placeholder=placeholder,
                            default_style=cn)
    if not submit:
        widget.addData('options', {'submit': True})
    if choices:
        field = forms.ChoiceField(attrname=input_name,
                                  required=False,
                                  choices=choices,
                                  widget=widget)
    else:
        field = forms.CharField(attrname=input_name,
                                required=False,
                                widget=widget)
    form_cls = forms.MakeForm(name,(field,))
    return forms.HtmlForm(form_cls,
                          inputs=submit,
                          layout=layout.FormLayout(default_style=deafult_style),
                          **kwargs)