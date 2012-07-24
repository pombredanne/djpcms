/*jslint evil: true, nomen: true, plusplus: true, browser: true */
/*globals jQuery*/
//
(function ($) {
    "use strict";
    //
    $.djpcms.decorator({
        name: 'input',
        defaultElement: '<input type="text">',
        selector: '.ui-input',
        config: {
            // If true, the input can submit the form when ENTER is pressed on it.
            submit: false,
            classes: {
                input: 'ui-input',
                control: 'control',
                focus: 'focus',
            }
        },
        _create: function () {
            var self = this,
                elem = self.element,
                config = self.config,
                prev;
            if (elem.is('input') || elem.is('textarea')) {
                // Create the wrapper
                elem.removeClass(config.classes.input);
                self.wrapper = $('<div></div>').addClass(config.classes.input);
                prev = elem.prev();
                if (prev.length) {
                    prev.after(self.wrapper);
                } else {
                    prev = elem.parent();
                    if (prev.length) {
                        prev.prepend(self.wrapper);
                    }
                }
                self.wrapper.append(elem).addClass(elem.attr('name'));
            } else {
                self.wrapper = elem;
                elem = self.wrapper.children('input,textarea');
                if (elem.length === 1) {
                    $.extend(true, config, elem.data('options'));
                    self.element = elem;
                }
            }
            self.element.focus(function () {
                self.wrapper.addClass(config.classes.focus);
            }).blur(function () {
                self.wrapper.removeClass(config.classes.focus);
            });
            // If the element has the submit-on-enter class, add
            // the keypressed event on ENTER to submit the form
            if (config.submit) {
                self.element.keypress(function (e) {
                    if (e.which === 13) {
                        var form = elem.closest('form');
                        if (form.length) {
                            form.submit();
                        }
                    }
                });
            }
        }
    });
    //
    $.djpcms.decorator({
        name: 'icon',
        defaultElement: 'i',
        sources: {
            fontawesome: function (self, icon) {
                if (!icon) {
                    icon = 'icon-question-sign';
                }
                self.element.prepend('<i class="' + icon + '"></i>');
            }
        },
        config: {
            source: 'fontawesome'
        },
        _create: function () {
            var config = this.config,
                source = this.sources[config.source],
                icon = config.icon;
            if (source) {
                if ($.isPlainObject(icon)) {
                    icon = icon[config.source];
                }
                source(this, icon);
            }
        }
    });
    //
    $.djpcms.decorator({
        name: 'button',
        defaultElement: '<button>',
        description: 'Add button like functionalities to html objects. It can handle anchors, buttons, inputs and checkboxes',
        selector: '.btn',
        config: {
            disabled: null,
            text: true,
            icon: null,
            classes: {
                button: 'btn',
                button_small: 'btn-small',
                button_large: 'btn-large',
                button_group: 'btn-group'
            }
        },
        _create: function () {
            var self = this,
                element = self.element.hide(),
                options = self.config,
                classes = options.classes,
                buttonElement,
                labelSelector,
                ancestor,
                toggle,
                children;
            if (element.is("[type=checkbox]")) {
                self.type = "checkbox";
            } else if (element.is("[type=radio]")) {
                self.type = "radio";
            } else if (element.is("input")) {
                self.type = "input";
            } else {
                self.type = "button";
            }
            // This is a checkbox
            if (self.type === "checkbox" || self.type === "radio") {
                toggle = true;
                labelSelector = "label[for='" + element.attr('id') + "']";
                ancestor = element.parents().last();
                buttonElement = ancestor.find(labelSelector);
                if (buttonElement) {
                    element.removeClass(classes.button);
                    buttonElement.attr('title', buttonElement.html());
                }
            } else {
                buttonElement = element;
            }
            if (buttonElement) {
                self.buttonElement = buttonElement;
                children = buttonElement.children();
                if (!options.text) {
                    buttonElement.html('');
                } else if (options.text !== true) {
                    buttonElement.html(options.text);
                }
                if (options.icon) {
                    self.ui('icon', buttonElement, {icon: options.icon});
                }
                buttonElement.addClass(classes.button).css('display', 'inline-block');
                if (toggle) {
                    self.refresh();
                    element.bind('change', function () {
                        self.refresh();
                    });
                }
            } else {
                self.destroy();
            }
        },
        refresh: function () {
            var self = this,
                classes = $.djpcms.options.widget.classes;
            if (self.element.prop("checked")) {
                $.djpcms.logger.debug('checked');
                self.buttonElement.addClass(classes.active);
            } else {
                $.djpcms.logger.debug('unchecked');
                self.buttonElement.removeClass(classes.active);
            }
        }
    });
}(jQuery));