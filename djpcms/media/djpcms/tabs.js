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
            effect: {
                name: 'fade',
                options: {},
                speed: 50
            },
            ajax: false,
            tabs: {
                //cookie: {expiry: 7},
            }
        },
        _create: function () {
            var config = this.config,
                effect = config.effect,
                options = config.tabs,
                element = this.element,
                current;
            if (config.ajax) {
                options = $.extend({
                    select: function(event, ui) {
                        current=ui;
                    },
                    load: function (event, ui) {
                        current=ui;
                        $(ui.panel).djpcms();
                    },
                    ajaxOptions: {
                        data: {
                            content_type: 'text/html'
                        },
                        success: function (xhr, status, index, anchor) {
                            //$(current.panel).append(xhr);
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
            element.tabs(options);
            if(effect.name) {
                element.show(effect.name, effect.options, effect.speed);
            } else {
                element.show();
            }
        }
    });
}(jQuery));