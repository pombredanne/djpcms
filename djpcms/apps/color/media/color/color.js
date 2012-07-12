/**
 * decorator for a colorpicker widget on a form input element
 */
(function($) {        
    $.djpcms.decorator({
        name:"color_picker",
        selector: 'input.color-picker',
        config: {
            parent_selector: '.color-picker'
        },
        colorize: function (color) {
            if(color) {
                if(color.substring(0,1) !== '#') {
                    color = '#'+color
                }
                this.element.css('background', color).parent(this.config.parent_selector).css('background',color);
            }
        },
        _create: function() {
            var self = this,
                options = $.extend({}, self.config);
            options.select = function(event, color) {
                self.colorize(color.formatted);
            };
            self.colorize(self.element.val());
            self.element.colorpicker(options);
        }
    });
}(jQuery));