from djpcms.forms import HtmlForm
from djpcms.forms.layout import uniforms
from .forms import ReportForm


HtmlReportForm = HtmlForm(
        ReportForm,
        layout = uniforms.Layout()
)