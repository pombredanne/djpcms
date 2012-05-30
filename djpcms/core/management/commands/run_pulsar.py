import djpcms
from djpcms.core.http import setResponseClass

try:
    from pulsar.apps import wsgi, test
    from pulsar import NOT_DONE, is_async, is_failure
    from djpcms.core.orms import OrmQuery

    class WSGIApplication(wsgi.WSGIApplication):
        
        def handler(self):
            website = self.callable
            middleware = website.wsgi_middleware()
            resp_middleware = website.response_middleware()
            return self.wsgi_handler(middleware, resp_middleware)
        
        
    class AsyncTestPlugin(test.Plugin):
        '''Plugin for testing djpcms with pulsar'''
        def startTest(self, test):
            test.web_site_callbacks.append(site_loader_callback)

except ImportError:
    WSGIApplication = None


class ResponseHandler(djpcms.ResponseHandler):
    '''An asynchronous djpcms response handler for pulsar.'''
    def not_done_yet(self):
        return NOT_DONE
        
    def async(self, value):
        if value is NOT_DONE:
            return True, NOT_DONE
        elif is_async(value):
            if not value.called:
                return True, value
            else:
                value = value.result
                if is_failure(value):
                    value.raise_all()
        elif isinstance(value,OrmQuery):
            query = value.query
            if query.called:
                value = query.result
            else:
                return True, query
        return False,value
    

def site_loader_callback(website):
    '''Set up pulsar handlers for djpcms.'''
    website.site.internals['response_handler'] = ResponseHandler()
    website.WSGIhandler = wsgi.WsgiHandler
    setResponseClass(wsgi.WsgiResponse)
    

class Command(djpcms.Command):
    help = "Starts a fully-functional Web server using pulsar."
    
    def run_from_argv(self, site_factory, command, argv):
        #Override so that we use pulsar parser
        self.execute(site_factory, argv)
        
    def handle(self, site_factory, argv):
        if WSGIApplication is None:
            print('To run this command you need to have pulsar installed')
            exit(0)
        site_factory.callbacks.append(site_loader_callback)
        site = site_factory()
        # get the full path of the setting file
        config = site.settings.path
        #website = pickle.loads(pickle.dumps(self.website))
        app = WSGIApplication(
                        callable = site_factory,
                        argv = argv,
                        config = config)
        app.cfg.djpcms_settings = site.settings
        site_factory.on_server_ready(app)
        app.start()
