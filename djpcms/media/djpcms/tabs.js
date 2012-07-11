/**
 * jQuery UI Tabs
 */
/*globals jQuery*/
(function ($) {
    "use strict";
    $.djpcms.decorator({
        name: "ui_tabs",
        selector: '.ui-tabs',
        config: {
            effect: 'drop',
            fadetime: 500,
            ajax: false
           //tabs: {cookie: {expiry: 7}},
        },
        _make: function () {
            var options = this.config;
            if (options.ajax) {
                //$('a',el.children('ul')).click(function(event) {
                //    event.preventDefault();
                //});
                //options.select = function(event, ui) {
                //    var a;
                //};
                options.load = function (event, ui) {
                    $(ui.panel).djpcms();
                };
                options.ajaxOptions = {
                    data: {content_type: 'text/html'},
                    complete: function (data, status) {
                        //if(status==='success') {
                        //    data.responseText = $(data.responseText).djpcms();
                        //}
                        //return data;
                    },
                    error: function (xhr, status, index, anchor) {
                        $(anchor.hash).html("Couldn't load this tab");
                    }
                };
            }
            this.element.tabs(options).show(options.effect, {}, options.fadetime);
        }
    });
}(jQuery));