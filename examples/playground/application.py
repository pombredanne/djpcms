from djpcms import views



def home_view(djp):
    return 'Testing'



class PlayGround(views.Application):
    home = views.View(renderer = home_view)