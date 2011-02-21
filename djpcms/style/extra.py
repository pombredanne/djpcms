from medplate import CssContext


def boxradius(radius, border = 2, measure = 'px'):
    r2 = '{0}{1}'.format(radius - border,measure)
    box = CssContext('box')
    hd = CssContext('box hd')
    bd = CssContext('box bd')
    ft = CssContext('box ft')
    box.data.update({'radius':'{0}{1}'.format(radius,measure)})
    hd.data.update({'radius_top_right':r2,
                    'radius_top_left':r2})
    bd.data.update({'radius_bottom_right':r2,
                    'radius_bottom_left':r2})
    ft.data.update({'radius_bottom_right':r2,
                    'radius_bottom_left':r2})