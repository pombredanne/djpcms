/*jslint evil: true, undef: true, browser: true */
/*globals jQuery*/

(function ($) {
    "use strict";
    //
    $.djpcms.decorator({
        name: 'button',
        widget: true,
        config: {
            disabled: null,
            text: true,
            icon: null,
            classes: {
                button: 'btn',
                button_small: 'btn-small',
                button_large: 'btn-large',
                button_group: 'btn-group',
            }
        },
        init: function() {
            var ui = $.djpcms.ui,
                self = this;
            //
            $.extend(ui, {
                // Add an icon to jQuery element elem
                addicon: function (elem, icon, icon_only) {
                    if ($.isPlainObject(icon)) {
                        icon = icon[ui.icons];
                    }
                    if (icon !== undefined) {
                        if (icon_only) {
                            elem.html('');
                        }
                        if (ui.icons === 'fontawesome') {
                            elem.prepend('<i class="' + icon + '"></i>');
                        }
                    }
                }
            });
        },
        decorate: function(container, config) {
            var options = config[this.name],
                elements = $('.'+options.classes.button, container);
            return this.many(elements, options);
        },
        _create: function () {
            var element = this.element(),
                classes = this.config.classes,
                labelSelector,
                ancestor;
            if (element.is("[type=checkbox]")) {
                this.type = "checkbox";
            } else if (element.is("[type=radio]")) {
                this.type = "radio";
            } else if (element.is("input")) {
                this.type = "input";
            } else {
                this.type = "button";
            }
            // This is a checkbox
            if (this.type === "checkbox" || this.type === "radio") {
                labelSelector = "label[for='" + $this.id + "']";
                ancestor = element.parents().last();
                buttonElement = ancestor.find(labelSelector);
                if (buttonElement) {
                    element.removeClass(classes.button);
                    buttonElement.attr('title', buttonElement.html());
                }
            } else {
                buttonElement = element;
            }
            buttonElement[0].element = element;
            if (!options.text) {
                buttonElement.html('');
            }
            ui.addicon(buttonElement, options.icon, !options.text);
            buttonElement.addClass(classes.button).css('display', 'inline-block');
        },
        _setup: function () {
            if (element.prop("checked")) {
                buttonElement.addClass(ui.classes.active);
            }
            buttonElement.click(function (e) {
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
    });
}(jQuery));