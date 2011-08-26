from djpcms import views, forms, html, ajax
from djpcms.forms.utils import saveform
from djpcms.forms.layout import uniforms as uni

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
    
    def stream(self, djp, widget, context):
        orig_data = widget.data_stream
        data = ((h[1],orig_data.pop(h[0],None)) for h in self.header1)
        yield html.DefinitionList(data_stream = data)\
                  .addClass(djp.settings.HTML.objectdef)\
                  .render(djp)
        
    

geo_entry = GeoEntry()


    
class geosearch(views.View):
    
    def render(self, djp):
        return self.get_form(djp).render(djp)
    
    def default_post(self, djp):
        '''handle the post request from the search'''
        return saveform(djp)

    def save(self, djp, f, commit = True):
        '''called by the search view. It doesn't save anything,
just perform the query.'''
        q = f.cleaned_data['q']
        res = self.appmodel.api.search(q)
        g = geo_entry.widget
        html = '\n'.join((g(data_stream = elem).render(djp) for elem in res))
        return ajax.jhtmls(html,'#geo-search-result')
    


class Geonames(views.Application):
    api = Geonames()
    search = geosearch(form = GeoSearchFormHtml,
                       in_navigation = 1)
    


def home_view(djp):
    return 'Testing'


class PlayGround(views.Application):
    home = views.View(renderer = home_view)
    
        