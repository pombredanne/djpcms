from djpcms.apps.included.admin import AdminApplication

from .models import WebAccount
from .forms import WebAccountForm



admin_urls = (
              AdminApplication('/webaccounts/',
                               WebAccount,
                               name = 'web accounts',
                               list_display = ['name','url','user','tags']),
            )