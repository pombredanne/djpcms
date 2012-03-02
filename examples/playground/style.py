from djpcms.style import css

CssContext('page-header',
           tag = '#page-header')

css('#page-footer',
    overflow = 'hidden',
    min_height = '200px',
    font_size = '90%',
    padding = '20px 0 0')

CssContext('geo-entry',
           tag = '.geo-entry',
           data = {
            'padding':'7px',
            'margin':'0 0 20px 0'
            },
            elems = [CssContext('geo-entry-def',
                        tag = '.object-definition',
                        data = {
                            'margin':'0'
                        })
                     ]
            )