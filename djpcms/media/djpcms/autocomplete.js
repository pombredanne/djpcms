/*jslint evil: true, nomen: true, plusplus: true, browser: true */
/*globals jQuery*/
//
(function ($) {
    "use strict";
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
                autocomplete: 'autocomplete'
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
        clean_data: function (terms, data) {
            var new_data = [];
            $.each(terms, function (i, val) {
                for (i = 0; i < data.length; i++) {
                    if (data[i].label === val) {
                        new_data.push(data[i]);
                        break;
                    }
                }
            });
            return new_data;
        },
        // The call back from the form to obtain the real data for
        // the autocomplete input field.
        get_real_data: function (multiple, separator) {
            var self = this;
            return function (val) {
                var data = '';
                if (multiple) {
                    data = [];
                    $.each(self.clean_data(self.split(val), this.data), function (i, d) {
                        data.push(d.value);
                    });
                    data = data.join(separator);
                } else if (val && this.data.length) {
                    data = this.data[0].real_value;
                }
                return data;
            };
        },
        // CAllback received when an element is selected
        add_data: function (item) {
            var self = this;
            if (self.config.multiple) {
                var terms = split(this.value);
                terms.pop();
                data = clean_data(terms, data);
                terms.push(display);
                new_data.push(item);
                terms.push("");
                display = terms.join(separator);
                real_data['data'] = data;
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
        _create: function () {
            var self = this,            
                opts = self.config,
                elem = this.element,
                name = elem.attr('name');
            opts.select = function (event, ui) {
                return self.add_data(ui.item);
            };
            // Bind to form pre-serialize 
            //elem.closest('form').bind('form-pre-serialize',
            //        $.proxy(self.get_autocomplete_data, self));
            self.widget = elem.parent('.' + $.djpcms.options.input.classes.input);
            if(!self.widget.length) {
                self.widget = elem;
            }
            opts.position = {of: self.widget};
            // Build the real (hidden) input
            if(opts.multiple) {
                self.real = $('<select name="'+ name +'[]" multiple="multiple"></select>');
                options.focus = function() {
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
                $.each(initials, function(i,initial) {
                    self.add_data({real_value: initial[0], value: initial[1]});
                });
            }
            // If choices are available, it is a local autocomplete.
            if (opts.choices && opts.choices.length) {
                var sources = [];
                $.each(choices,function(i,val) {
                    sources[i] = {value:val[0],label:val[1]};
                });
                options.source = function( request, response ) {
                    if(multiple) {
                        response( $.ui.autocomplete.filter(
                            sources, split(request.term).pop() ) );
                    }
                    else {
                        return sources;
                    }
                },
                elem.autocomplete(options);
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
}(jQuery));