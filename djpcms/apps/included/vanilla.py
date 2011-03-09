from djpcms import views


class Application(views.ModelApplication):
    search = views.SearchView()
    add    = views.AddView()
    view   = views.ViewView()
    edit   = views.ChangeView()
    delete = views.DeleteView()