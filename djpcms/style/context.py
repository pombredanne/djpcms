from djpcms.contrib.medplate import CssContext

#________________________________________ BREADCRUMBS
CssContext('breadcrumbs',
           tag = 'div.breadcrumbs',
           template = 'djpcms/style/breadcrumbs.css_t',
           data = {
                   'font_size': '130%',
                   'padding': '10px 0'}
           )