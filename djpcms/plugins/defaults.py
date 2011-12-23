from djpcms import forms, views, html
from djpcms.plugins import DJPplugin

layouts = (
           ('v','vertical'),
           ('o','orizontal')
           )
dlayouts = dict(layouts)

class navigationForm(forms.Form):
    levels = forms.ChoiceField(choices = ((1,1),(2,2)))
    layout = forms.ChoiceField(choices = (('v','vertical'),
                                          ('o','orizontal')))


class SoftNavigation(DJPplugin):
    '''Display the site navigation from the closest "soft" root
 for a given number of levels.'''
    name = 'soft-nav'
    description = 'Navigation'
    form = navigationForm
    
    def render(self, request, wrapper, prefix, levels = 1,
               layout = 'v', **kwargs):
        nav_element = html.Widget('div', cn = dlayouts[layout])
        nav = views.Navigator(soft = True, levels = int(levels),
                              nav_element = nav_element)
        return nav.render(request)