from djpcms import cms

class Command(cms.Command):
    help = "Load the environment."
    
    def handle(self, options):
        self.website()