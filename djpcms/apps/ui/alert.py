from djpcms.media.style import *

cssv.alert.padding = spacing(6, 10)
cssv.alert.background = color('#FCF8E3')
cssv.alert.color = color('#C09853')
cssv.alert.radius = cssv.body.radius
cssv.alert.border.color = darken(cssv.alert.background, 5)
cssv.alert.border.style = None
cssv.alert.border.width = cssv.border.width

cssv.alert_error.background = color('#F2DEDE')
cssv.alert_error.color = color('#B94A48')
cssv.alert_error.border.color = darken(cssv.alert_error.background, 5)
cssv.alert_error.border.style = cssv.alert.border.style
cssv.alert_error.border.width = cssv.alert.border.width


############################################################    ALERTS
css('.alert',
    gradient(cssv.alert.background),
    radius(cssv.alert.radius),
    border(**cssv.alert.border.params()),
    cssa('.alert-error',
         gradient(cssv.alert_error.background),
         border(**cssv.alert_error.border.params()),
         color=cssv.alert_error.color),
    color=cssv.alert.color,
    padding=cssv.alert.padding)