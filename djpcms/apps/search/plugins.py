from djpcms import html, plugins, forms, ImproperlyConfigured
from djpcms.plugins.apps import FormModelForm
from djpcms.forms.utils import get_form

from .search import get_search_url

class SearchModelForm(FormModelForm):
    autocomplete = forms.BooleanField()
    multiple = forms.BooleanField(initial = True)
    tooltip  = forms.CharField(required = False, max_length = 50)


class SearchBox(plugins.DJPplugin):
    '''A text search for a model rendered as a nice search input.
    '''
    name = 'search-box'
    description = 'Search your Models'
    form = SearchModelForm
    
    def render(self, request, wrapper, prefix,
               for_model = None, method = 'get',
               tooltip = None, ajax = False,
               autocomplete = False,
               multiple = False,  **kwargs):
        url = get_search_url(request, for_model)
        if not url:
            raise ImproperlyConfigured('No search engine installed with site.\
 Cannot add search plugin. You need to install one!\
 Check documentation on how to do it.')
        w = get_form(djp, HtmlSearchForm).addAttr('action',url)\
                                         .addAttr('method',method)
        if tooltip:
            w.form.dfields['q'].help_text = tooltip
        if ajax:
            w.addClass(forms.AJAX)
        else:
            w.removeClass(forms.AJAX)
        return w.render(request)

