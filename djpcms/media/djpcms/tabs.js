
    /**
     * jQuery UI Tabs
     */
(function ($) {
    $.djpcms.decorator({
        name: "ui_tabs",
        config: {
            effect:'drop',
            fadetime: 500,
           //tabs: {cookie: {expiry: 7}},
        },
        decorate: function(container, config) {
            var c = config.ui_tabs;
            $('.ui-tabs', container).each(function() {
                var el = $(this),
                    data = el.data(),
                    options = {};
                if(data.ajax) {
                    //$('a',el.children('ul')).click(function(event) {
                    //    event.preventDefault();
                    //});
                    //options.select = function(event, ui) {
                    //    var a;
                    //};
                    options.load = function(event, ui) {
                        $(ui.panel).djpcms();
                    };
                    options.ajaxOptions = {
                            data: {content_type:'text/html'},
                            complete: function(data, status) {
                                //if(status==='success') {
                                //    data.responseText = $(data.responseText).djpcms();
                                //}
                                //return data;
                            },
                            error: function(xhr, status, index, anchor) {
                                $( anchor.hash ).html(
                                    "Couldn't load this tab. We'll try to fix this as soon as possible. " +
                                    "If this wouldn't be a demo." );
                            }
                    };
                }
                el.tabs(options).show(c.effect,{},c.fadetime);
            });
        }
    });
}(jQuery));