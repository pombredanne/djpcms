from djpcms import views, forms, html, ajax
from djpcms.forms.utils import saveform
from djpcms.forms.layout import uniforms as uni
from djpcms.apps import static

from .geonames import Geonames

    
class GeoSearchForm(forms.Form):
    q = forms.CharField(label = 'search text')
        

GeoSearchFormHtml = forms.HtmlForm(
       GeoSearchForm,
       inputs = (('search','search'),),
       layout = uni.Layout(uni.Columns('q','submits'),
                           html.Html(tag = 'div', id = 'geo-search-result'),
                           default_style = uni.nolabel)
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
        
    

geo_entry = GeoEntry()


    
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
    

def home_view(request):
    return 'Testing'


class Geonames(views.Application):
    api = Geonames()
    search = geosearch(form=GeoSearchFormHtml, in_nav=1)


class PlayGround(views.Application):
    home = views.View(renderer = home_view)
    favicon = static.FavIconView()
    
        