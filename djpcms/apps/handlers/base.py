from djpcms import sites


class BaseSiteHandler(object):
    
    def __init__(self, site):
        self.site = site
        
    