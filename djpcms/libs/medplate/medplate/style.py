from medplate import CssContext


CssContext('field-widget-input',
           tag = '.field-widget.input',
           template = 'djpcms/style/field-widget.css_t',
           data = {
                   'padding': '0.3em'
                   }
)

CssContext('button-submit',
           tag = 'input.ui-button',
           data = {
                   'padding': '0.3em 0.5em'
                   }
)