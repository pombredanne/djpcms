


class Application(object):
    code = None
    name = None
    
    def __init__(self, config = None):
        if not config:
            from djpcms import sites
            config = sites.settings
        self.config = config
        
    def setup(self):
        self.setup_extensions()
        
    def setup_extensions(self):
        return
        if self.config:
            for extension in self.config['extensions']:
                self.setup_extension(extension)
            
    def setup_extension(self, extension):
        pass