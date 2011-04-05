from djpcms.forms import HtmlForm
from djpcms.forms.layout.uniforms import Layout, Columns, Fieldset, Inputs
from .forms import ReportForm


HtmlReportForm = HtmlForm(
        ReportForm,
        layout = Layout(Columns(
            (Fieldset('tags', 'allow_comments','slug'),),
            (Fieldset('title', 'abstract', 'body'),),
            (Fieldset('visibility','markup','timestamp',),Inputs(default_style  = 'blockLabels')),
            template = 'djpcms/inner/cols3_25_50_25.html'
        ))
)