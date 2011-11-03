from djpcms import views

from .contactform import ContactForm


class ContactView(views.View):
    
    def render(self, djp, **kwargs):
        return self.get_form(djp).render(djp)
    
    def default_post(self, djp):
        return appview.saveform(djp)
    
    def save(self, request, f):
        return f.save()
    
    def success_message(self, instance, flag):
        return "Your message has been sent. Thank you!"


class ContactUs(views.Application):
    name = 'Contact Us'
    contact = ContactView(isplugin = True,
                          form = ContactForm)