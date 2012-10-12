/**
 * AUTOCOMPLETE
 *
 * The actual values are stored in the data attribute of the input element.
 * The positioning is with respect the "widgetcontainer" parent element if
 * available.
 */
$.djpcms.decorator({
    name: "autocomplete",
    defaultElement: '<input>',
    selector: 'input.autocomplete',
    config: {
        classes: {
            autocomplete: 'autocomplete',
            list: 'multiSelectList',
            container: 'multiSelectContainer'
        },
        removelink: function (self) {
            return $('<a href="#"><i class="icon-remove"></i></a>');
        },
        minLength: 2,
        maxRows: 50,
        search_string: 'q',
        separator: ', ',
        multiple: false
    },
    split: function (val) {
        return val.split(/,\s*/);
    },
    // Callback received when an element is selected
    add_data: function (item) {
        var self = this;
        if (self.config.multiple) {
            self.addOption(item);
        } else {
            self.real.val(item.real_value);
            self.element.val(item.value);
            //this.real.data('value', item.value);
        }
        return false;
    },
    get_autocomplete_data: function (jform, options, veto) {
        var value = this.element.val();
        if(this.multiple) {
            //
        } else {
            if (this.real.data('value') !== value) {
                this.real.val(value);
            }
        }
    },
    // Add a new option to the multiselect element
    addOption: function (elem) {
        var self = this,
            list = self.list,
            selections = list.data('selections'),
            options = self.config,
            item = $('<li>'),
            opt = $('<option>', {
                text: elem.label,
                val: elem.real_value
            }),
            val = opt.val();
        if (selections.indexOf(val) === -1) {
            self.real.append(opt);
            selections.push(val);
            item.append($('<span>', {html: elem.label}))
                .append(options.removelink(self))
                .data('option', opt).appendTo(self.list);
            if (self.list.children().length) {
                self.list_container.show();
            }
            opt.prop('selected', true);
            self.element.val('');
        }
    },
    //
    dropListItem: function (li) {
        var opt = li.data('option'),
            selections = this.list.data('selections'),
            idx;
        li.remove();
        if (this.list.children().length === 0) {
            this.list_container.hide();
        }
        idx = selections.indexOf(opt.val());
        if (idx !== -1) {
            selections.splice(idx, 1);
        }
        opt.remove();
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
            list = $('<div>', {'class': classes.input}).addClass(options.classes.container).append(self.list);
        } else {
            //container.prepend(element.after(container));
        }
        self.list_container = list.hide();
        container.append(self.list_container);
    },
    //
    _create: function () {
        var self = this,
            opts = self.config,
            elem = this.element,
            name = elem.attr('name'),
            name_len = name.length;
        opts.select = function (event, ui) {
            return self.add_data(ui.item);
        };
        self.wrapper = elem.parent('.' + $.djpcms.options.input.classes.input);
        if(!self.wrapper.length) {
            self.wrapper = null;
        }
        opts.position = {of: self.wrapper || elem};
        // Build the real (hidden) input
        if(opts.multiple) {
            if (name.substring(name_len-2, name_len) === '[]') {
                name = name.substring(0, name_len-2);
            }
            self.real = $('<select name="'+ name +'[]" multiple="multiple"></select>');
            self.list = $('<ul>').data('selections', []).addClass(opts.classes.list);
            self.buildDom();
            //
            self.list.delegate('a', 'click', function(e) {
                e.preventDefault();
                self.dropListItem($(this).closest('li'));
                return false;
            });
            //
            opts.focus = function() {
                return false;
            };
            elem.bind("keydown", function( event ) {
                if ( event.keyCode === $.ui.keyCode.TAB &&
                        $( this ).data( "autocomplete" ).menu.active ) {
                    event.preventDefault();
                }
            });
        } else {
            self.real = $('<input name="'+ name +'"></input>');
        }
        elem.attr('name', name + '_proxy').before(self.real.hide());
        if (opts.initials_value) {
            $.each(opts.initials_value, function(i, initial) {
                self.add_data({real_value: initial[0], value: initial[1]});
            });
        }
        // If choices are available, it is a local autocomplete.
        if (opts.choices && opts.choices.length) {
            var sources = [];
            $.each(opts.choices, function(i, val) {
                sources[i] = {value:val[0], label:val[1]};
            });
            opts.source = function( request, response ) {
                if(opts.multiple) {
                    throw('Not implemented');
                    //response( $.ui.autocomplete.filter(
                    //    sources, split(request.term).pop() ) );
                }
                else {
                    return sources;
                }
            };
            elem.autocomplete(opts);
        } else if(opts.url) {
            // We have a url, the data is obtained remotely.
            opts.source = function(request, response) {
                var ajax_data = {
                        style: 'full',
                        maxRows: opts.maxRows,
                        'search_string': opts.search_string
                    },
                    loader;
                ajax_data[opts.search_string] = request.term;
                loader = $.djpcms.ajax_loader(opts.url, 'autocomplete', 'get', ajax_data);
                $.proxy(loader, response)();
            };
            elem.autocomplete(opts);
        } else {
            self.warn('Could not find choices or url for autocomplete data');
        }
    }
});
//
$.djpcms.addJsonCallBack({
    id: "autocomplete",
    handle: function (data, response) {
        response($.map(data, function (item) {
            return {
                value: item[0],
                label: item[1],
                real_value: item[2]
            };
        }));
    }
});
