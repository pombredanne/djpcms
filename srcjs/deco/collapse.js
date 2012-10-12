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
            options: {},
            duration: 10
        },
        icons: {
            open: {
                fontawesome: 'plus-sign'
            },
            close: {
                fontawesome: 'minus-sign'
            }
        }
    },
    _create: function () {
        var self = this,
            classes = $.djpcms.options.widget.classes;
        self.widget = self.element.closest('.' + classes.widget);
        self.body = self.widget.find('.' + self.config.classes.collapsable).first();
        if(self.body.length) {
            self.toggle();
            self.element.mousedown(function (e) {
                e.stopPropagation();
            }).click(function () {
                self.widget.toggleClass('collapsed');
                self.toggle();
                return false;
            });
        }
    },
    toggle: function () {
        var self = this,
            be = self.config.effect,
            icons = self.config.icons,
            el = self.element.html('');
        if (self.widget.hasClass('collapsed')) {
            self.body.hide(be.type, be.options, be.duration, function () {
                $.djpcms.ui.icon(el, {icon: icons.open});
            });
            self.info('closed body');
        } else {
            self.body.show(be.type, be.options, be.duration, function () {
                $.djpcms.ui.icon(el, {icon: icons.close});
            });
            self.info('opened body');
        }
    }
});