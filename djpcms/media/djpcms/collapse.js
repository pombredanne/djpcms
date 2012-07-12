/*jslint evil: true, nomen: true, plusplus: true, browser: true */
/*globals jQuery*/
(function ($) {
    "use strict";
    $.djpcms.decorator({
        name: "collapsable",
        description: "Decorate box elements",
        selector: 'a.collapse',
        config: {
            classes: {
                collapsable: 'bd'
            },
            effect: {
                type: 'blind',
                duration: 10
            },
            icons: {}
        },
        _create: function () {
            var self = this,
                classes = $.djpcms.options.widget.classes,
                element = self.element,
                be = self.config.effect,
                icons = self.config.icons,
                widget = element.closest('.' + classes.widget),
                bd = widget.find('.' + self.config.classes.collapsable).first();
            if(bd.length) {
                element.mousedown(function (e) {
                    e.stopPropagation();
                }).click(function () {
                    var el = $(this);
                    if (widget.hasClass('collapsed')) {
                        widget.removeClass('collapsed');
                        bd.show(be.type, {}, be.duration, function () {
                            el.html(icons.close);
                        });
                        self.info('opened body');
                    } else {
                        widget.addClass('collapsed');
                        bd.hide(be.type, {}, be.duration, function () {
                            el.html(icons.open);
                        });
                        self.info('closed body');
                    }
                    return false;
                });
            }
        }
    });
}(jQuery));