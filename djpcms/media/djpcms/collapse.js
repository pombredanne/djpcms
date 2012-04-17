(function ($) {
    "use strict";
    $.djpcms.decorator({
        id:"djpcms_widget",
        description:"Decorate box elements",
        config: {
            selector: '.widget.collapsable',
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
                    be = config.box_effect,
                    bd = $('.bd',cp).first();
                if(cp.hasClass('collapsed')) {
                    bd.show(be.type,{},be.duration,function(){
                        cp.removeClass('collapsed');
                        self.html(icons.close);
                    });
                }
                else {
                    bd.hide(be.type,{},be.duration, function(){
                        cp.addClass('collapsed');
                        self.html(icons.open);
                    });
                }
                return false;
            });
        }
    });
}(jQuery));