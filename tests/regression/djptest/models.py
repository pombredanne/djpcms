from djpcms import forms

from regression import models

if models.Model:
    
    class Strategy(models.Model):
        name     = models.CharField(unique = True, max_length = 200)
        description = models.TextField()
        
        def __unicode__(self):
            return self.name
    
    
    class StrategyForm(forms.Form):
        name = forms.CharField()
        description = forms.CharField(required = False)
    
