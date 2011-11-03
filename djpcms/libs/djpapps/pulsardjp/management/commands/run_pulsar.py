import djpcms

from pulsardjp import WSGIApplication


class Command(djpcms.Command):
    help = "Starts a fully-functional Web server using pulsar."
    
    def run_from_argv(self, site_factory, command, argv):
        #Override so that we use pulsar parser
        self.execute(site_factory, argv)
        
    def handle(self, site_factory, argv):
        WSGIApplication(callable = site_factory,
                        argv = argv).start()
