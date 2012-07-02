from djpcms.cms import request_processor


@request_processor
def ie_media(request):
    request.media.add_css({'all':
                           [('fontawesome/font-awesome-ie7.css', 'IE 7')]})