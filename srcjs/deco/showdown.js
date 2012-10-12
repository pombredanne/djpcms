/*globals Showdown*/
$.djpcms.decorator({
    name: "showdown",
    selector: '.markdown',
    _create: function () {
        var md = this.config.markdown,
            converter;
        if(md && Showdown) {
            converter = new Showdown.converter();
            md = converter.makeHtml(md);
        }
        this.element.html(md);
    }
});