from djpcms.apps.handlers import DjpCmsHandler
from .server import Server


def serve(port = 0, **kwargs):
    '''Create the application serving a django site'''
    if withpool:
        pool = getpool(0)
    else:
        pool = None
    server = Server(DjpCmsHandler, port)
    server.build()
    media = settings.MEDIA_URL
    if media and not media.startswith('http'):
        django_media(server.root,settings,path)
    return server.serve()
