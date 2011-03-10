from djpcms.forms import HtmlForm
from djpcms.forms.layout.uniforms import Fieldset, Layout, blockLabels2

from .forms import ContactForm


HtmlContactForm = HtmlForm(
        ContactForm,
        layout = FormLayout(Fieldset('name','email'),
                            Fieldset('body',css_class = blockLabels2)),
        submits = (('Send message','contact'),)
)
