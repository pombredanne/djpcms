/**
 * decorator for a colorpicker widget on a form input element
 */
(function($) {        
    $.djpcms.decorator({
        id:"color_picker",
        config: {
            selector: 'input.color-picker',
            parent_selector: '.color-picker'
        },
        decorate: function($this, config) {
            var opts = config.color_picker;
            
            function colorize(el, color) {
                if(color) {
                    if(color.substring(0,1) !== '#') {
                        color = '#'+color
                    }
                    el.css('background',color).parent(opts.parent_selector).css('background',color);
                }
            }
            
            $(opts.selector, $this).each(function() {
                var el = $(this),
                    options = el.data();
                colorize(el, el.val());
                if(options.select === undefined) {
                    options.select = function(event, color) {
                        colorize($(this), color.formatted);
                    };
                }
                colorize(el, el.val());
                el.colorpicker(options);
            });
        }
    });
}(jQuery));