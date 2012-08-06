/*
 * Djpcms decorator for filtering models. This decorator
 * is used by the Filtering plugin in djpcms.cms.plugins
 *
 */
/*jslint evil: true, nomen: true, plusplus: true, browser: true */
/*globals jQuery*/
(function ($) {
    "use strict";
    if ($.djpcms.ui.modelFilters === undefined) {
        $.djpcms.decorator({
            name: 'modelFilters',
            selector: '.model-filters',
            dataType: 'json',
            config: {
                model_selector: 'select.for-model, input.for-model',
                fields_selector: 'select.model-fields'
            },
            _create: function () {
                var self = this,
                    options = self.config,
                    elem = self.element,
                    model_element = $(options.model_selector, elem),
                    model_fields = $(options.fields_selector, elem);
                if (model_element.length === 1) {
                    model_element.change(function () {
                        self._get_fields(model_element, model_fields);
                    });
                    self._get_fields(model_element, model_fields);
                } else {
                    self.warn('Could not find model element.');
                }
            },
            _get_fields: function (model_element, model_fields) {
                var self = this,
                    element = model_element,
                    href,
                    submit_data,
                    opts;
                if (model_element.is('select')) {
                    element = $(':selected', model_element);
                }
                if (element.length) {
                    href = element.data('href');
                    self.model = element.val();
                    if (self.model && href) {
                        submit_data = $.djpcms.ajaxparams('fields');
                        opts = {
                            url: href,
                            type: 'get',
                            dataType: self.config.dataType,
                            data: submit_data
                        };
                        self.info('Submitting ajax ' + opts.type + ' request "fields"');
                        opts.success = function (data, s) {
                            if (data.header === 'fields') {
                                self._refresh(data.body, model_fields);
                            }
                        };
                        $.ajax(opts);
                    } else {
                        self._refresh([], model_fields);
                    }
                }
            },
            _refresh: function (fields, model_fields) {
                var self = this;
                $.each(model_fields, function () {
                    var el = $(this),
                        selected = [],
                        skip = [],
                        multiple = el.prop('multiple'),
                        dfields;
                    // First we handle the selected element
                    $.each($(':selected', el), function () {
                        selected.push(this.value);
                    });
                    el.empty();
                    el.append($('<option>', {html: '-------------'}).val(''));
                    // For multiple select, add selected values first so we preserve order.
                    if(multiple && selected) {
                        dfields = {};
                        $.each(fields, function (i, field) {
                            dfields[field.code] = field;
                        });
                        $.each(selected, function (i, value) {
                            var field = dfields[value];
                            if (field) {
                                $('<option>', {html: field.text}).val(field.code).prop('selected', true).appendTo(el);
                                skip.push(value);
                            }
                        });
                        selected = [];
                    }
                    $.each(fields, function (i, field) {
                        var code = field.code,
                            opt;
                        if (skip.indexOf(code) === -1) {
                            opt = $('<option>', {html: field.text}).val(field.code);
                            el.append(opt);
                            if (selected.indexOf(code) !== -1) {
                                opt.prop('selected', true);
                            }
                        }
                    });
                    el.trigger('change');
                });
            }
        });
    }
}(jQuery));