(function ($) {
    "use strict";
    $.djpcms.decorator({
        id:"djpcms_widget",
        description:"Decorate box elements",
        config: {
            selector: '.widget.collapsable',
            effect: {type:"blind",duration:10},
        },
        decorate: function($this, config) {
            var opts = config.djpcms_widget,
                bname = '.hd',
                elems = $(opts.selector,$this);
            $('a.collapse',elems).mousedown(function (e) {
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