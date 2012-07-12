/**
 * jQuery UI Tabs
 * requires jQuery UI
 */
/*globals jQuery*/
(function ($) {
    "use strict";
    /**
     * Accordion menu
     */
    $.djpcms.decorator({
        name: "accordion",
        selector: '.ui-accordion-container',
        config: {            
            effect: null,//'drop',
            fadetime: 200,
            autoHeight: false,
            fillSpace: false
        },
        _create: function () {
            var element = this.element,
                opts = this.config;
            element.accordion(opts).show(opts.effect, {}, opts.fadetime);
        }
    });
    /**
     * Tabs
     */
    $.djpcms.decorator({
        name: "ui_tabs",
        selector: '.ui-tabs',
        config: {
            effect: 'drop',
            fadetime: 500,
            ajax: false
           //tabs: {cookie: {expiry: 7}},
        },
        _create: function () {
            var options = this.config;
            if (options.ajax) {
                options = $.extend({
                    load: function (event, ui) {
                        $(ui.panel).djpcms();
                    },
                    ajaxOptions: {
                        data: {
                            content_type: 'text/html'
                        },
                        complete: function (data, status) {
                            //if(status==='success') {
                            //    data.responseText = $(data.responseText).djpcms();
                            //}
                            //return data;
                        },
                        error: function (xhr, status, index, anchor) {
                            $(anchor.hash).html("Couldn't load this tab");
                        }
                    }
                }, options);
            }
            this.element.tabs(options).show(options.effect, {}, options.fadetime);
        }
    });
}(jQuery));