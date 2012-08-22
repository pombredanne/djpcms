/*jslint evil: true, nomen: true, plusplus: true, browser: true */
/*globals jQuery*/
(function ($) {
    "use strict";
    if ($.djpcms.ui.zclip === undefined) {
        // Not yet defined. register it
        $.djpcms.decorator({
            name: 'zclip',
            selector: '.zclip',
            defaultElement: '<span>',
            plugins: {},
            config: {
            	icon: {fontawesome: 'copy'},
            	title: 'Copy to clipboard',
            	text: true
            },
            _create: function () {
                var self = this,
                    options = self.config,
                    text = self.element.attr('title') || '',
                    title = options.title + ' ' + text,
                    a = $('<a>');
                $.djpcms.ui.icon(a.attr('title', title), {icon: options.icon});
                self.element.prepend(a.show());
                a.zclip({
                	path: $.djpcms.options.media_url+'djpcms/zclip/ZeroClipboard.swf',
                	copy: function () {
                		return text;
                	}
                });
            }
        });
    }
}(jQuery));