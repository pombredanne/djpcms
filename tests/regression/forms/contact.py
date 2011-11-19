import unittest as test

from djpcms import forms, html
from djpcms.apps.contactus import ContactForm


def dummy_send(**kwargs):
    pass


class TestFormValidation(test.TestCase):
    
    def testContantForm(self):
        d = ContactForm(data = {'body':'blabla'}, send_message = dummy_send)
        self.assertFalse(d.is_valid())
        self.assertEqual(len(d.errors),2)
        self.assertEqual(d.errors['name'], ['Name is required'])
        self.assertEqual(d.errors['email'], ['E-mail is required'])
        d = ContactForm(data = {'body':'blabla','name':''},
                        send_message = dummy_send)
        self.assertFalse(d.is_valid())
        self.assertEqual(len(d.errors),2)
        self.assertTrue('name' in d.errors)
        d = ContactForm(data = {'body':'blabla','name':'pippo',
                                'email':'pippo@pippo.com'},
                        send_message = dummy_send)
        self.assertTrue(d.is_valid())