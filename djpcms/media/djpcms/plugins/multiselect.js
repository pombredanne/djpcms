/*
 * Djpcms decorator for a better multiple select
 *
 */
/*jslint evil: true, nomen: true, plusplus: true, browser: true */
/*globals jQuery*/
(function ($) {
    "use strict";
    if ($.djpcms.ui.multiSelect === undefined) {
        // Not yet defined. register it
        $.djpcms.decorator({
            name: 'multiSelect',
            selector: 'select[multiple="multiple"]',
            config: {
                classes: {
                    proxy: 'proxySelect',
                    list: 'multiSelectList',
                    container: 'multiSelectContainer',
                    disabled: 'disabled'
                },
                select_list_suffix: '-select-list',
                extractLabel: function (opt) {
                    return opt.html();
                },
                removelink: function (self) {
                    return $('<a href="#"><i class="icon-remove"></i></a>');
                },
                title: 'Select...',
                animate: true,
                highlight: true,
                sortable: false,
                plugins: []
            },
            _create: function () {
                var self = this,
                    options = self.config,
                    classes = $.djpcms.options.input.classes,
                    element = self.element,
                    wrapper = element.parent('.' + classes.input),
                    id = element.attr('id');
                // build the proxy select element
                if (wrapper.length) {
                    self.wrapper = wrapper;
                } else {
                    self.wrapper = null;
                }
                self.proxy = $('<select>', {'class': options.classes.proxy})
                                .append($('<option value=""></option>')
                                .text(element.attr('title') || options.title));
                // Build the item list
                if (id) {
                    self.list = $('#' + id + options.select_list_suffix);
                    if (!self.list.length) {
                        self.list = null;
                    }
                }
                if (!self.list) {
                    self.list = $('<ul>');
                }
                self.list.addClass(options.classes.list).empty();
                // Set events
                self.proxy.change(function (e, o) {
                    self.selectChangeEvent(e, o);
                }).click(function (e, o) {
                    self.selectClickEvent(e, o);
                });
                element.hide().after(self.proxy);
                // the item list needs to be placed below the select
                if (self.list.parent().length === 0) {
                    self.buildDom();
                }
                // Loop over options and add selected items to the item list
                element.children().each(function () {
                    var el = $(this);
                    if (el.is('option')) {
                        self.addOption(el);
                    } else if (el.is('optgroup')) {
                        self.addOptionGroup(el);
                    }
                });
            },
            // Add a new option to the proxy element
            addOption: function (elem) {
                var self = this,
                    opt = $('<option>', {
                        text: elem.text(),
                        val: elem.val()
                    }).appendTo(self.proxy).data('original', elem),
                    selected = elem.is(':selected'),
                    disabled = elem.is(':disabled');
                if (selected && !disabled) {
                    self.addListItem(opt);
                    self.disableSelectOption(opt);
                } else if (!selected && disabled) {
                    self.disableSelectOption(opt);
                }
            },
            addOptionGroup: function (elem) {

            },
            //
            disableSelectOption: function (opt) {
                var self = this;
                opt.addClass(self.config.classes.disabled)
                    .removeAttr('selected')
                    .attr('disabled', 'disabled');
                if ($.browser.msie && $.browser.version < 8) {
                    self.proxy.hide().show();
                } // this forces IE to update display
            },
            // Add a selected option to the item list
            addListItem: function (opt) {
                var self = this,
                    item = $('<li>'),
                    original = opt.data('original'),
                    options = self.config;
                if (!original) {
                    return;
                }
                item.append($('<span>', {html: options.extractLabel(opt)}))
                    .append(options.removelink(self))
                    .data('option', opt).appendTo(self.list);
            },
            //
            buildDom: function () {
                var self = this,
                    options = self.config,
                    classes = $.djpcms.options.input.classes,
                    container = $('<div>', {'class': options.classes.container}),
                    list = self.list;
                if (self.wrapper) {
                    self.wrapper.after(container);
                    container.addClass(classes.control)
                             .prepend(self.wrapper.removeClass(classes.control));
                    list = $('<div>', {'class': classes.input}).append(self.list);
                } else {
                    container.prepend(element.after(container));
                }
                container.append(list);
            }
        });
    }
}(jQuery));