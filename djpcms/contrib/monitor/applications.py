from djpcms.contrib.monitor import views


class StdnetMonitorApplication(views.Application):
    name = 'Stdnet Monitor'
    list_per_page = 100
    
    home  = views.RedisHomeView(isplugin = True, isapp = True)
    db    = views.RedisDbView(regex = '(?P<db>\d+)', isapp = True)
    flush = views.RedisDbFlushView(regex = 'flush', parent = 'db')
    
    def dburl(self, db):
        dbview = self.getview('db')
        djp = view(request, db = db)
        return djp.url
    
    
class StdModelApplication(views.ModelApplication):
    search      = views.SearchView()
    information = views.StdModelInformationView(regex = 'info')
    flush       = views.StdModelDeleteAllView(regex = 'flush')