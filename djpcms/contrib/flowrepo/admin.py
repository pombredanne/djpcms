from djpcms.apps.included.admin import AdminApplication

from .models import WebAccount, Report
from .forms import WebAccountForm



admin_urls = (
              AdminApplication('/webaccounts/',
                               WebAccount,
                               name = 'web accounts',
                               list_display = ['name','url','user','tags']),
              ContentApplication('/content/',
                                 Report,
                                 list_display = ['name','description','parent'])
            )