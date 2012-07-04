from djpcms import media
from djpcms.cms import request_processor

extra_media = media.Media(css={'all':
                               [('fontawesome/font-awesome-ie7.css', 'IE 7')]})

@request_processor
def ie_media(request):
    request.view.add_media(request, extra_media)