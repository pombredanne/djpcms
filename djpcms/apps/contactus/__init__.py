from djpcms import views

from .contactform import HtmlContactForm


class ContactUs(views.Application):
    name = 'Contact Us'
    contact = views.AddView('/', has_plugins=True, form=HtmlContactForm)