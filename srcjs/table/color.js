/**
 * DJPCMS Decorator for jQuery dataTable plugin
 */
$.djpcms.decorator({
    name: "color_number",
    selector: 'tr .color',
    config: {
        classes: {
            negative: 'ui-state-error-text',
            arrow: 'arrow'
        },
        icons: {
            up: {
                'fontawesome': 'icon-arrow-up',
                'jquery': 'ui-icon-arrowthick-1-n'
            },
            down: {
                'fontawesome': 'icon-arrow-down',
                'jquery': 'ui-icon-arrowthick-1-s'
            }
        }
    },
    _create: function () {
        var el = this.element,
            config = this.config,
            classes = config.classes,
            val = el.html();
        try {
            val = parseFloat(val);
            if (val < 0) {
                el.addClass(classes.negative);
            }
            if (el.hasClass(classes.arrow)) {
                if (val > 0) {
                    this.ui('icon', el, {icon: config.icons.up});
                } else if (val < 0) {
                    this.ui('icon', el, {icon: config.icons.up});
                }
            }
        } catch (e) {}
    }
});
