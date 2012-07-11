from djpcms import views, media

html = '''\
<h2 id="qunit-banner"></h2>
<div id="qunit-testrunner-toolbar"></div>
<h2 id="qunit-userAgent"></h2>
<ol id="qunit-tests"></ol>
<div id="qunit-fixture">test markup, will be hidden</div>
<div id="testcontainer"></div>'''

class JsTestView(views.View):
    _media = media.Media(
            js = ['http://code.jquery.com/qunit/git/qunit.js',
                  'jstests/base.js'],
            css = {'screen': ['http://code.jquery.com/qunit/git/qunit.css']})
    
    def linkname(self, request):
        return 'js unit'
    
    def title(self, request):
        return 'Javascript unit tests'
    
    def render(self, request, **kwargs):
        return html
    
    def media(self, request):
        return self._media
    
    
class Application(views.Application):
    home = JsTestView()