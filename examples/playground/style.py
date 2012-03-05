from djpcms.style import css

css('#page-header')

css('#page-footer',
    overflow = 'hidden',
    min_height = '200px',
    font_size = '90%',
    padding = '20px 0 0')

css('.geo-entry',
    css('.object-definition', margin = 0),
    padding = '7px',
    margin = '0 0 20px 0')