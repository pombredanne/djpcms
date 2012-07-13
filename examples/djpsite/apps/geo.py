import json

from djpcms import views, forms, html, ajax
from djpcms.forms import layout as uni
from djpcms.utils import orms
from djpcms.utils.httpurl import HttpClient
from djpcms.apps import search

class Geo(orms.Model):
    '''A simple model for querying the geonames database.'''
    search_url = 'http://ws.geonames.org/searchJSON?'
    
    def __init__(self, id=None, name='', countryCode='', **kwargs):
        self.id = id
        self.name = name
        self.countryCode = countryCode
        for k in kwargs:
            setattr(self, k, kwargs[k])
        
    def __str__(self):
        return '%s - %s' % (self.name, self.countryCode)
    
    @classmethod
    def http(cls):
        return HttpClient()
        
    @classmethod
    def search(cls, q):
        c = cls.http()
        body = {'q': q,
                'maxRows': 20,
                'lang': 'en',
                'style': 'short'}
        response = c.get(cls.search_url, data=body)
        if response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))
            qs = []
            all = set()
            for data in data['geonames']:
                id = data.pop('geonameId', None)
                if id:
                    el = cls(id=id, **data)
                    re = str(el)
                    if re not in all:
                        all.add(re)
                        qs.append(el)
            return qs
        
        
           
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

    

    