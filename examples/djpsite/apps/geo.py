from djpcms import views, forms, html, ajax
from djpcms.forms import layout as uni
from djpcms.utils import orms
from djpcms.apps import search

class Geo(orms.Model):
    '''A simple model for querying the geonames database.'''
    search_url = 'http://ws.geonames.org/searchJSON?'
    
    @classmethod
    def filter(cls, q=None, maxRows = 10, **kwargs):
        http = self.httpclient
        body = urlencode({'q': q,'maxRows': maxRows,
                          'lang': 'en',
                          'style': 'full'})
        response = http.request(self.search_url,body)
        if response.status == 200:
            data = json.loads(response.content.decode('utf-8'))
            if not data['geonames']:
                return None
            return data['geonames'][:maxRows]
        
           
class GeoSearchForm(forms.Form):
    q = forms.ChoiceField(choices=search.Search(
                                    autocomplete=True,
                                    search=True,
                                    model=Geo),
                          label='Type a geographical place')
        

GeoSearchFormHtml = forms.HtmlForm(
       GeoSearchForm,
       inputs=(),
       layout=uni.FormLayout(default_style=uni.nolabel)
)


class GeoEntry(html.WidgetMaker):
    tag = 'div'
    default_class = 'geo-entry ui-widget-content'
    header1 = (('name','Name'),
               ('population','Population'),
               ('countryName','Country'),
               ('countryCode','Country code'),
               ('adminName1','Region'),
               ('adminName2','Administration')
               )
    
    def stream(self, request, widget, context):
        orig_data = widget.data_stream
        data = ((h[1],orig_data.pop(h[0],None)) for h in self.header1)
        yield html.DefinitionList(data_stream = data)\
                  .addClass(request.settings.HTML.objectdef)\
                  .render(request)


class Application(views.Application):
    form = GeoSearchFormHtml
    search = views.SearchView()
    view = views.ViewView()
    
    def render(self, request, query=None, **context):
        # Render the search view
        return self.get_form(request, **context).render(request)
        
    def render_instance_default(self, request, instance, **kwargs):
        # render the default instance view
        maker = GeoEntry()
        return maker(instance=instance, appmodel=self)

    
class geosearch(views.View):
    
    def render(self, request):
        return self.get_form(request).render(request)
    
    def default_post(self, request):
        '''handle the post request from the search'''
        return saveform(request)

    def save(self, request, f, commit = True):
        '''called by the search view. It doesn't save anything,
just perform the query.'''
        q = f.cleaned_data['q']
        res = self.appmodel.api.search(q)
        if res:
            g = geo_entry.widget
            html = '\n'.join((g(data_stream = elem).render(request) for elem in res))
        else:
            html = '<p>Your search - <b>{0}</b> -\
 did not match any documents.</p>'.format(q)
        return ajax.jhtmls(html,'#geo-search-result')
    

    