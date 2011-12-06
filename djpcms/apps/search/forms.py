from djpcms import html, forms, views
from djpcms.forms import layout


class SearchForm(forms.Form):
    q = forms.CharField(
                attrname = forms.SEARCH_STRING,
                required = False,
                widget = html.TextInput(
                        default_class = 'classy-search autocomplete-off',
                        title = 'Enter your search text'))


SearchSubmit = html.WidgetMaker(
                    tag = 'div',
                    default_class='cx-submit',
                    inner = html.Widget('input:submit',
                                        cn='cx-search-btn '+forms.NOBUTTON,
                                        title = 'Search').render())

HtmlSearchForm = forms.HtmlForm(
        SearchForm,
        inputs = [SearchSubmit],
        layout = layout.FormLayout(
                    layout.SubmitElement(tag = None),
                    layout.DivFormElement('q', default_class = 'cx-input'),
                    tag = 'div',
                    default_style = layout.nolabel,
                    default_class = 'cx-search-bar'
            )
)