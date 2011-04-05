from django.contrib.contenttypes.models import ContentType
from djpcms.apps.included.tagging import TagField
from djpcms.utils import markups
from djpcms import forms
from djpcms.utils import json


visibility_choices = (
        (0, 'Hidden'),              
        (1, 'Private'),          # In draft, availoable to view only to authors
        (2, 'Authenticated'),    # authenitaced users only
        (3, 'Public'),
    )


def get_upload_model(file):
    '''Upload model'''
    try:
        from PIL import Image
    except ImportError:
        import Image

    model = models.Attachment
    try:
        if file.content_type.split('/')[0] == 'image':
            model = models.Image
        #trial_image = Image.open(file)
        #trial_image.load()
        #trial_image.verify()
        #model = models.Image
    except:
        model = models.Attachment
    
    return model



class FlowForm(forms.Form):
    '''General form for a flowitem'''
    timestamp = forms.DateTimeField(required = False)
    tags = TagField(required = False)
    allow_comments = forms.BooleanField()
    visibility = forms.ChoiceField(choices=visibility_choices, initial=3)
        
    def save(self, commit = True):
        user       = self.get_user()
        model      = self._underlying
        instance   = self.instance
        instance.content_type = ContentType.objects.get_for_model(model)
        flowitems  = models.FlowItem.objects
        registered = flowitems.unregisterModel(model)
        if instance.object_id:
            object     = instance.object
        else:
            object     = model()
        instance.object_id = self.savemodel(object).id
        instance   = super(FlowForm,self).save(commit = commit)
        instance.authors.add(user)
        if registered:
            flowitems.registerModel(model)
        return instance


class FlowFormMarkup(FlowForm):
    markup      = forms.ChoiceField(choices=markups.choices(),
                                    default=markups.default())


class FlowFormRelated(FlowForm):
    '''handle related items as multiple choice field'''
    #related_items = forms.ModelMultipleChoiceField(queryset = models.FlowItem.objects.all(), required = False)
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance',None)
        if instance:
            initial = kwargs.get('initial',None) or {}
            initial['related_items'] = [obj.related.id for obj in instance.following.all()]
            kwargs['initial'] = initial
        super(FlowFormRelated,self).__init__(*args, **kwargs)
            
    def save(self, commit = True):
        instance = super(FlowFormRelated,self).save(commit = True)
        if commit:
            instance.following.all().delete()
            for related in self.cleaned_data['related_items']:
                instance.follow(related)
        return instance
    

class ReportForm(FlowFormMarkup):
    '''The Report Form'''
    title = forms.CharField()
    abstract = forms.CharField(widget = forms.TextArea(cn = 'taboverride'), required = False)
    body = forms.CharField(widget = forms.TextArea(cn = 'taboverride'), required = False)
    slug = forms.CharField(required = False)
        
    def save(self, commit = True):
        obj.name = self.cleaned_data['title']
        obj.description = self.cleaned_data['abstract']
        obj.body = self.cleaned_data['body']
        obj.save()
        return obj   
    

class UploadForm(FlowForm):
    elem = forms.FileField(label = 'file')
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance',None)
        if instance:
            self._underlying = instance.content_type.model_class()
        super(UploadForm, self).__init__(*args, **kwargs)
        
    def savemodel(self, obj):
        obj.name = self.instance.name
        obj.elem = self.cleaned_data['elem']
        obj.save()
        return obj        
    
    def clean_elem(self):
        file = self.cleaned_data.get('elem')
        model = get_upload_model(file)
        if self._underlying and model is not self._underlying:
            raise forms.ValidationError('Cannot change upload type')
        self._underlying = model
        return file


class FlowItemSelector(forms.Form):
    '''
    Form for selecting items to display
    '''
    #content_type = forms.ModelMultipleChoiceField(queryset = models.FlowItem.objects.allmodels,
    #                                              label = 'types',
    #                                              required = False)
    item_per_page = forms.IntegerField(initial = 10)
        
    def save(self, commit = True):
        pass

        
class WebAccountForm(forms.Form):
    '''A form to add/edit web accounts.
    '''
    name = forms.CharField()
    url = forms.CharField()
    username = forms.CharField(required = False)
    password = forms.CharField(required = False)
    email    = forms.EmailField(required = False)
    pin      = forms.CharField(required = False)
    extended = forms.CharField(required = False)
    tags     = TagField(required = False)
    
    def get_user(self):
        if not self.user or self.user.is_authenticated():
            return None
        else:
            return self.user
        
    def clean(self):
        user = self.get_user()
        if not user:
            raise forms.ValidationError('Not authenticated')
    
    def clean_name(self, name):
        user = self.get_user()
        if not user:
            return name
        acc = self.mapper.filter(user = user, name = name)
        if acc:
            acc = acc[0]
            if acc.id != self.instance.id:
                raise forms.ValidationError('Account %s already available' % name)
            return name
        else:
            return name
        
    def save(self, commit = True):
        if commit:
            data = self.cleaned_data.copy()
            for n in ('user','name','url','tags'):
                data.pop(n)
            self.instance.data = json.dumps(data)
        return super(WebAccountForm,self).save(commit)
    
    
class ChangeImage(forms.Form):
    image   = forms.ChoiceField(choices = lambda : models.Image.objects.all)
    class_name = forms.CharField(max_length = 100, required = False)
    
    
def add_related_upload(file, instance, name = None, description = ''):
    item = instance.flowitem()
    if not item or not file:
        return
    model = get_upload_model(file)    
    name = name or file.name
    obj = model(elem = file, name = name, description = description)
    obj.save()
    return models.FlowRelated.objects.create_for_object(item,obj)
    
    
    
