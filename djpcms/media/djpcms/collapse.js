(function ($) {
    "use strict";
    $.djpcms.decorator({
        name: "collapsable",
        description: "Decorate box elements",
        selector: '.ui-widget.collapsable',
        config: {
            effect: {type:"blind",duration:10},
        },
        _create: function() {
            var element = this.element,
                opts = this.options;
            element.mousedown(function (e) {
                e.stopPropagation();    
            }).click(function() {
                var self = $(this),
                    cp = self.parents(opts.selector).first(),
                    data = cp.data(),
                    icons = data.icons,
                    be = opts.effect,
                    bd = $('.bd',cp).first();
                if(cp.hasClass('collapsed')) {
                    cp.removeClass('collapsed');
                    bd.show(be.type,{},be.duration,function(){
                        self.html(icons.close);
                    });
                }
                else {
                    cp.addClass('collapsed');
                    bd.hide(be.type,{},be.duration, function(){
                        self.html(icons.open);
                    });
                }
                return false;
            });
        }
    });
}(jQuery));