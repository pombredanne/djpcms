/*globals window, document, jQuery, console*/
/*jslint nomen: true, plusplus: true */
//
(function ($) {
    "use strict";
    //
    $.djpcms.decorator({
        name: "textselect",
        selector: 'select.text-select',
        description: "A select widget with text to display",
        _create: function() {
            var elems = $(config.textselect.selector,$this);
            // The selectors
            function text(elem) {
                var me = $(elem),
                    val = me.val(),
                    target = me.data('target');
                if(target) {
                    $('.target',target).hide();
                    if(val) {
                        $('.target.'+val,target).show();
                    }
                }
            }
            $.each(elems,function() {
                var me = $(this),
                    target = me.data('target');
                if(target) {
                    var t = $(target,$this);
                    if(!t.length) {
                        t = $(target)
                    }
                    if(t.length) {
                        me.data('target',t);
                        text(me);
                    }
                    else {
                        me.data('target',null);
                    }
                }
            });
            elems.change(function(){text(this)});
        }
    });
}(jQuery));