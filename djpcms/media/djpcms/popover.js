/*jslint nomen: true, plusplus: true, browser: true */
/*global jQuery: true, ColVis: true */
/**
 * djpcms - dataTable integration utilities
 */
(function ($) {
    "use strict";
    //
    $.djpcms.decorator({
        name: "popover",
        selector: '.pop-over, .label',
        config: {
            x: 10,
            y: 30,
            predelay: 400,
            effect: 'fade',
            fadeOutSpeed: 200,
            position: "top"
        },
        _create: function () {
            if ($.fn.popover) {
                var self = this,
                    el = self.element,
                    des = el.data('content');
                if (des) {
                    el.attr('rel', 'popover');
                    el.popover();
                }
            } else {
                this.destroy();
            }
        }
    });
}(jQuery));