from djpcms.apps.included.admin import AdminApplication

from .models import Strategy, StrategyForm


admin_urls = (
              AdminApplication('/strategy/',
                               Strategy,
                               form = StrategyForm),
            )