from djpcms import forms, html
from djpcms.utils import test

class UserForms(test.TestCase):

    def testUserChangeForm(self):
        '''Test the UserChangeForm which provides boolean fields which
by default are true and some which are false.'''
        from djpcms.apps.user import UserChangeForm
        initials = dict(UserChangeForm.initials())
        self.assertEqual(initials,{'is_active':True})
        html_form = forms.HtmlForm(UserChangeForm)
        fw = html_form()
        text = fw.render()
        self.assertTrue("type='checkbox'" in text)
        self.assertTrue("checked='checked" in text)
    
    @test.skipUnless(test.djpapps,"Requires djpapps installed")
    def testUserChangeFormWidthModel(self):
        '''Test the UserChangeForm which provides boolean fields which
by default are true and some which are false.'''
        from djpcms.apps.user import UserChangeForm
        from sessions import User
        html_form = forms.HtmlForm(UserChangeForm, model = User)
        fw = html_form()
        text = fw.render()
        self.assertTrue("type='checkbox'" in text)
        self.assertTrue("checked='checked" in text)
    
