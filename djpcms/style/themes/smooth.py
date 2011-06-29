#
#   SMOOTH THEME
#
from medplate import CssTheme
from djpcms.style.roller import make_theme

theme_name = 'smooth'


smooth = {
          'body':{'color':'#222222',
                  'background':'#ffffff'},
          'flatbox': {'background':'#ffffff',
                      'border':'1px solid #4297d7'},
          'widget-anchor': {'color':'#026890',
                            'color_hover':'#6eac2c',
                            'text_decoration': 'none',
                            'weight':'normal'},
          'breadcrumbs': {'color':'#333333'},
          'field-widget-input': {'background':'#ffffff',
                                 'border':'1px solid #a6c9e2'},
          'box':{},
          # Uniform
          'uniform label':{'font_weight': 'bold',
                           'color': '#666666'},
          'tablerelated-legend': {'font_size': '110%',
                                  'font_weight':'bold',
                                  'color': '#666666'
                                  },
          # Tablesorter
          'tablesorter': {'head_border_color':'#fff',
                          'body_border_color':'#a6c9e2',
                          'odd_background_color':'#dbebeb',
                          'row_hover_background':'#d0e5f5'},
           # dataTable
           'datatable': {'odd_background_color':'#f2f2f2',
                         'even_background_color':'transparent',
                         'even_sort_background':'#fcefa1',
                         'odd_sort_background':'#f7eeb5'},
           #
           # Navigation
          'nav': {'main_text_shadow': '0 2px 2px rgba(0, 0, 0, 0.5)',
                  'secondary_text_shadow': 'none',
                  # SHADOW OF DROP DOWN MENU
                  'secondary_border_color':'#b4b4b4',
                  'drop_down_shadow': '10px 10px 5px rgba(0,0,0, .5)',
                  'font_weight': 'bold',
                  'color': '#E7E5E5',
                  'background':'transparent',
                  'hover_background':'#79c9ec',
                  'secondary_hover_background':'#c2c2c2',
                  #'active_background':'#dcdcdc',
                  #'active_color':'#dcdcdc',
                  'hover_color': '#444',
                  'selected_color':'#444',
                  #'padding': '2px 0',     # Padding for outer ul
                  'height': '30px',
                  'inner_radius': '10px',
                  'list_margin': '0 5px',
                  'anchor_padding': '0 20px',
                  'radius': '14px'},
           'edit_plugin_body': {'background':'#BAE28D'}
           }

make_theme(theme_name,smooth)
