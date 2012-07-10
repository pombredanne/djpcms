(function ($) {
    "use strict";
    $.djpcms = (function (djpcms) {
        var ui = djpcms.ui,
            classes = ui.classes;
        classes.button = 'btn';
        classes.button_small = 'btn-small';
        classes.button_large = 'btn-large';
        classes.button_group = 'btn-group';
        //
        ui.addicon = function (el, icon, icon_only) {
            if ($.isPlainObject(icon)) {
                icon = icon[ui.icons];
            }
            if (icon !== undefined) {
                if (icon_only) {
                    el.html('');
                }
                if (ui.icons === 'fontawesome') {
                    el.prepend('<i class="' + icon + '"></i>');
                }
            }
        };
        //
        ui.button = function (elem, options) {
            var ui = $.djpcms.ui,
                options = options || {};
            $.each($(elem), function () {
                var element = $(this).hide(),
                    labelSelector,
                    ancestor;
                if (this.type === "checkbox" || this.type === "radio") {
                    labelSelector = "label[for='" + this.id + "']";
                    ancestor = element.parents().last();
                    this.buttonElement = ancestor.find(labelSelector);
                    if (this.buttonElement) {
                        this.buttonElement.attr('title', this.buttonElement.html());
                        this.buttonElement[0].element = element[0];
                        if (element.prop("checked")) {
                            this.buttonElement.addClass(classes.active);
                        }
                        this.buttonElement.click(function(e) {
                            e.preventDefault();
                            this.element.checked = !this.element.checked;
                            if (this.element.checked) {
                                $.djpcms.logger.debug('checked');
                                $(this).addClass(classes.active);
                            } else {
                                $.djpcms.logger.debug('unchecked');
                                $(this).removeClass(classes.active);
                            }
                        });
                    }
                } else {
                    this.buttonElement = element;
                }
                if (options.text) {
                    this.buttonElement.html(options.text);
                }
                ui.addicon(this.buttonElement, options.icon, options.icon_only);
                this.buttonElement.addClass(classes.button).show();
            });
        };
        // Decorator
        djpcms.decorator({
            id: 'button',
            decorate: function ($this, config) {
                ui.button($('.' + classes.button, $this));
            }
        });
        // Return djpcms
        return djpcms;
    }($.djpcms || {}));
    
}(jQuery));