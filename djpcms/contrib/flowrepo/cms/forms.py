from django.contrib.auth.models import User

from djpcms.utils import markups
from djpcms.contrib.flowrepo.models import FlowItem, Attachment, Image
from djpcms.contrib.flowrepo.forms import WebAccountForm, UploadForm, FlowForm, ReportForm

from djpcms.forms import FormWidget
from djpcms.forms.layout.uniforms import Layout, Fieldset, Html, inlineLabels, blockLabels2
from djpcms.html import HtmlWrap, box


CRL_HELP = HtmlWrap('div', 
                    inner = HtmlWrap('div', inner = markups.help()).addClass('body')
                   ).addClass('flowitem report').render()


collapse = lambda title, html, c, cl: box(hd = title, bd = html, collapsable = c, collapsed = cl)


__all__ = ['FlowForm','NiceWebAccountForm','NiceUloaderForm','NiceReportForm']



#_________________________________________________________ UNIFORMS

NiceWebAccountForm = FormWidget(
                                WebAccountForm,
                                Layout(Fieldset('name', 'url', 'tags', elem_css = blockLabels2),
                                       Fieldset('username', 'password', 'email','pin', elem_css = blockLabels2)
                                       )
                                )
    
    
NiceUloaderForm = FormWidget(
                             UploadForm,
                             Layout(Fieldset('visibility', 'tags', 'name', elem_css = inlineLabels),
                                    Fieldset('elem','description', elem_css = blockLabels2),
                                    )
                             )
    

NiceReportForm = FormWidget(
                            ReportForm,
                            Layout(
                                   Fieldset('title', 'abstract', 'body', key = 'body'),
                                   Fieldset('visibility', 'allow_comments', elem_css = inlineLabels),
                                   Fieldset('tags', 'authors', elem_css = blockLabels2),
                                   Fieldset('related_items',
                                            elem_css = blockLabels2,
                                            key = 'related_items',
                                            renderer = lambda html : collapse('Related Items',html,True,False)),              
                                   Fieldset('slug', 'timestamp', 'markup',
                                            key = 'metadata',
                                            renderer = lambda html : collapse('Metadata',html,True,True)), 
                                   Html(CRL_HELP, key = 'help',
                                      renderer = lambda html : collapse('Writing Tips',html,True,True)),
                                   template = 'flowrepo/report-form-layout.html'
                                   ),
                            js = ('djpcms/taboverride.js',)
                            )


    