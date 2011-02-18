
body_defaults = { 
    'background': '#fff',
    'color': '#000',
    #
    'font_family': "Helvetica,Arial,'Liberation Sans',FreeSans,sans-serif",
    'font_size': '14px',
    'font_weight': 'normal',
    'font_style': 'normal',
    'line_height': '1.3em',
    'text_align': 'left',
    #
    'block_spacing': '15px'
    }
   

def jqueryui(context, loader, style):
    style = style or 'smooth'
    base  = 'jquery-ui-css/{0}/'.format(style)
    data = loader.render(base + 'jquery-ui.css')
    toreplace = 'url(images'
    media_url = context['MEDIA_URL']
    replace = 'url({0}djpcms/'.format(media_url) + base + 'images'
    lines = data.split(toreplace)
    def jquery():
        yield lines[0]
        for line in lines[1:]:
            p = line.find(')')
            if p:
                line = replace + line
            else:
                line = toreplace + line
            yield line
    return ''.join(jquery())
    
