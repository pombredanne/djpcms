from medplate import CssContext

CssContext('writing-title',
           tag = '.flowrepo-report .field-widget.title input',
           data = {
            'font_size': '150%'
        }
)

CssContext('writing-abstract',
           tag = '.flowrepo-report .field-widget.abstract textarea',
           data = {
            'height': '4em'
        }
)

CssContext('writing-body',
           tag = '.flowrepo-report .field-widget.body textarea',
           data = {
            'min_height': '400px'
        }
)