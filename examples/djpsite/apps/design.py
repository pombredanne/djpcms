from djpcms import forms, views


class DesignApplication(views.Application):
    home = views.View()
    forms_view = views.View('/forms')