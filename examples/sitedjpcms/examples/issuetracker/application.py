from djpcms import forms
from djpcms.forms.layout.uniforms import Layout, blockLabels 
from djpcms.views import appview
from djpcms.apps.included import archive

from .models import Issue


class AddEditIssueForm(forms.Form):
    description = forms.CharField()
    body = forms.CharField(widget = forms.TextArea)
    tags = forms.CharField(required = False)
    
    def before_save(self, commit = True):
        cd = self.cleaned_data
        tags = cd.pop('tags')
        cd['user'] = self.request.user

hform = forms.HtmlForm(AddEditIssueForm,
                       layout = Layout(default_style = blockLabels))


class IssueTraker(archive.ArchiveApplication):
    inherit = True
    date_code = 'timestamp'
    STATUS_CODES = (
                    (1, 'Open'),
                    (2, 'Working'),
                    (3, 'Closed'),
                    )
    PRIORITY_CODES = (
                      (1, 'Bloker'),
                      (2, 'Critical'),
                      (3, 'High'),
                      (4, 'Medimu'),
                      (5, 'Low'),
                      )
    add = appview.AddView(form = hform,
                          redirect_to_view = 'search',
                          force_redirect = True)
    view = appview.ViewView()
    edit = appview.ChangeView(form = hform,
                              redirect_to_view = 'search',
                              force_redirect = True)
    delete = appview.DeleteView()
    
    

    

    

    