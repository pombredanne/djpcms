from djpcms.apps.included.admin import AdminApplication

from .models import WebAccount, Report
from .forms import WebAccountForm, ReportForm



admin_urls = (
              AdminApplication('/webaccounts/',
                               WebAccount,
                               form = WebAccountForm,
                               name = 'web accounts',
                               list_display = ['name','url','user','tags']),
              AdminApplication('/content/',
                               Report,
                               form = ReportForm,
                               name = 'content',
                               list_display = ['name','description','parent'])
            )