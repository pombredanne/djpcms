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
                //
                self.list.delegate('a', 'click', function(e) {
                    e.preventDefault();
                    self.dropListItem($(this).closest('li'));
                    return false;
                });
            },
            //
            selectClickEvent: function (e, o) {},
            selectChangeEvent: function (e, o) {
                var proxy_opt = $('option:selected:eq(0)', this.proxy);
                this.addListItem(proxy_opt);
            },
            // Add a new option to the proxy element
            addOption: function (elem) {
                var self = this,
                    opt = $('<option>', {
                        text: elem.text(),
                        val: elem.val()
                    }).appendTo(self.proxy).data('original', elem),
                    selected = elem.prop('selected'),
                    disabled = elem.prop('disabled');
                if (selected && !disabled) {
                    self.addListItem(opt);
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
            //
            enableSelectOption: function (proxy_opt) {
                var self = this,
                    opt = proxy_opt.data('original');
                proxy_opt.removeClass(self.config.classes.disabled)
                    .prop('selected', false)
                    .prop('disabled', false);
                opt.prop('selected', false);
            },
            // Add a selected option to the item list
            addListItem: function (proxy_opt) {
                var self = this,
                    item = $('<li>'),
                    opt = proxy_opt.data('original'),
                    options = self.config;
                if (!opt) {
                    return;
                }
                item.append($('<span>', {html: options.extractLabel(proxy_opt)}))
                    .append(options.removelink(self))
                    .data('option', proxy_opt).appendTo(self.list);
                if (self.list.children().length) {
                    self.list_container.show();
                }
                self.disableSelectOption(proxy_opt);
                opt.prop('selected', true);
            },
            dropListItem: function (li) {
                var proxy_opt = li.data('option');
                this.enableSelectOption(proxy_opt);
                li.remove();
                if (this.list.children().length === 0) {
                    this.list_container.hide();
                }
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
                self.list_container = list.hide();
                container.append(self.list_container);
            }
        });
    }
}(jQuery));