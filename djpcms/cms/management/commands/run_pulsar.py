from pulsar.apps import wsgi, test
from pulsar import NOT_DONE, is_async, is_failure

import djpcms
from djpcms import cms


class WSGIServer(wsgi.WSGIServer):

    def handler(self):
        website = self.callable
        middleware = website.wsgi_middleware()
        resp_middleware = website.response_middleware()
        return self.wsgi_handler(middleware, resp_middleware)


class AsyncTestPlugin(test.Plugin):
    '''Plugin for testing djpcms with pulsar'''
    def startTest(self, test):
        test.web_site_callbacks.append(site_loader_callback)


class Command(cms.Command):
    help = "Starts a fully-functional Web server using pulsar."

    def get_options(self):
        #Override so that we use pulsar parser
        return self.argv

    def handle(self, argv, start=True):
        website = self._website
        site = self.website(argv)
        # get the full path of the setting file
        config = site.settings.path
        #website = pickle.loads(pickle.dumps(self.website))
        app = WSGIServer(callable=website,
                         description=site.settings.DESCRIPTION,
                         epilog=site.settings.EPILOG,
                         argv=argv,
                         version=website.version or djpcms.__version__,
                         config=config)
        #app.cfg.djpcms_settings = site.settings
        callback = getattr(website, 'on_pulsar_app_ready', None)
        if callback:
            callback(app)
        if start:
            app.start()
        else:
            return app

    def setup_logging(self, settings, options):
        pass
