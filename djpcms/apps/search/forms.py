from djpcms import html, forms, views
from djpcms.forms import layout


def search_form(name = 'SearchForm', placeholder = 'search', input_name = None,
                submit = None, cn = None, choices = None, **kwargs):
    '''Create a new :class:`djpcms.forms.HtmlForm` for searching.
    
:parameter name: name of the :class:`Form`
'''
    if cn:
        cn += ' submit-on-enter'
    else:
        cn = 'submit-on-enter'
    input_name = input_name or forms.SEARCH_STRING
    widget = html.TextInput(placeholder = placeholder,
                            default_style = cn)
    
    if choices:
        field = forms.ChoiceField(attrname = input_name,
                                  required = False,
                                  choices = choices,
                                  widget = widget)
    else:
        field = forms.CharField(attrname = input_name,
                                required = False,
                                widget = widget)
    form_cls = forms.MakeForm(name,(field,))
    submit = submit or []
    return forms.HtmlForm(form_cls,
                          inputs = submit,
                          layout = layout.FormLayout(),
                          **kwargs)