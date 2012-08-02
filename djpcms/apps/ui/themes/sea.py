from djpcms.media.style import *

mighty_stale = '#556270'
storm_sky = '#909daa'
azzurro = '#87B0DB'
new_door = 'fcffc0'
white = '#fafafa'
mighty_stale_darker = color.darken(mighty_stale, 15)
storm_sky_dark = color.darken('#909daa', 10)
storm_sky_darker = color.darken('#909daa', 20)

with cssv.theme('sea') as t:
    t.widget.head.background = azzurro
    t.clickable.default.background = ('v', storm_sky, storm_sky_dark)
    t.clickable.default.border.color = storm_sky_dark
    t.clickable.default.color = white
    t.clickable.hover.background = ('v', storm_sky_dark, storm_sky)
    t.clickable.hover.border.color = storm_sky_darker
    t.clickable.active.background = storm_sky_darker
    t.clickable.active.border.color = storm_sky

    # topbar
    t.topbar.default.background = ('v', mighty_stale, mighty_stale_darker)
    cssv.topbar.active.background = mighty_stale_darker