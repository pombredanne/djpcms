from djpcms import forms, html, ajax, media
from djpcms.forms import layout


class UploadForm(forms.Form):
    files = forms.FileField(multiple = True)

    def on_submit(self, commit):
        results = []
        for appmodel in sites.for_model(self.model):
            storage = appmodel.site.storage
            if storage:
                for file in self.cleaned_data['files']:
                    name = storage.save(file)
                    if commit:
                        instance = appmodel.save_file(name,file)
                        delete_url = None
                        view = appmodel.getview('delete')
                        if view:
                            view = view(self.request, instance = instance)
                            delete_url = view.url
                        results.append({"name":name,
                                        "size":file.size,
                                        "url":storage.url(name),
                                        'delete_url':delete_url,
                                        "delete_type":"POST"})
                       #"thumbnail_url":thumb_url,
        return ajax.simplelem(results)


class FileInputHtml(layout.FieldTemplate):
    tag = 'div'
    default_class = "fileupload-buttonbar"
    _media = media.Media(js = [media.jquerytemplate(),
                                'fileupload/jquery.fileupload.js',
                                'fileupload/jquery.fileupload-ui.js',
                                'fileupload/upload.js'],
            css = {'screen':['fileupload/jquery.fileupload-ui.css']})

    def stream(self, djp, widget, context):
        yield '<label class="fileinput-button">\
<span>Add files...</span>\
{0[inner]}\
</label>\
<button type="submit" class="start">Start upload</button>\
<button type="reset" class="cancel">Cancel upload</button>\
<button type="button" class="delete">Delete files</button>'.format(context)

    def media(self, djp = None):
        return self._media


FileUploadForm = forms.HtmlForm(
        UploadForm,
        ajax = False,
        layout = layout.FormLayout(layout.FormLayoutElement('files', tag = None,
                                    field_widget_maker = FileInputHtml),
                            form_messages_container_class = None),
        inputs = []
)