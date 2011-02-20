from random import randint
from djpcms import forms


class SimpleForm(forms.Form):
    name = forms.CharField(max_length = 64)
    age = forms.IntegerField(default = lambda b : randint(10,100))
    profession = forms.ChoiceField(choices = ((1,'student'),
                                              (2,'professional'),
                                              (3,'artist')), required = False)
    
    

class DataForm(forms.Form):
    city = forms.CharField(max_length = 64)
    date_of_birth = forms.DateField()
    
    simple = SimpleForm

