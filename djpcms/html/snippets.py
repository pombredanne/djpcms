from djpcms import media
from .base import WidgetMaker

__all__ = ['CopyToClipBoard']

CopyToClipBoard = WidgetMaker(tag='span',
                              cn='zclip',
                              media=media.Media(
                                js = ['djpcms/zclip/jquery.zclip.js',\
                                      'djpcms/plugins/zclip.js']))
                                    