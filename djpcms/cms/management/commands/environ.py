import djpcms

class Command(djpcms.Command):
    help = "Load the environment."
    
    def handle(self, options):
        self.website()