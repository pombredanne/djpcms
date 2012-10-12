/**
 * Ajax links, buttons, select and forms
 *
 * Decorate elements for jQuery ui if the jquery flag is true (default).
 * and apply ajax functionality where required.
 */
$.djpcms.decorator({
    name: "ajax",
    description: "add ajax functionality to links, buttons, selects and forms",
    defaultElement: '<a>',
    selector: 'a.ajax, button.ajax, select.ajax, form.ajax, input.ajax',
    config: {
        dataType: "json",
        classes: {
            submit: 'submitted',
            autoload: "autoload"
        },
        confirm_actions: {
            'delete': 'Please confirm delete',
            'flush': 'Please confirm flush'
        },
        effect: {
            name: 'fade',
            options: {},
            speed: 50
        },
        form: {
            iframe: false,
            beforeSerialize: function (jqForm, opts) {
                return true;
            },
            beforeSubmit: function (formData, jqForm, opts) {
                var self = jqForm[0].djpcms_widget,
                    ok = !self.disabled;
                if (ok) {
                    self.disabled = true;
                    $.each($.djpcms.before_form_submit, function () {
                        formData = this(formData, jqForm);
                    });
                    jqForm.addClass(self.config.classes.submit);
                }
                return ok;
            },
            success: function (o, s, xhr, jqForm) {
                var self = jqForm[0].djpcms_widget;
                return self.finished(o, s, xhr);
            },
            error: function (o, s, xhr, jqForm) {
                var self = jqForm[0].djpcms_widget;
                return self.finished(o, s, xhr);
            }
        },
        timeout: 30
    },
    _create: function () {
        var self = this,
            element = self.element;
        self.disabled = false;
        if (element.is('select')) {
            self.type = 'select';
            self.create_select();
        } else if (element.is('input')) {
            self.type = 'input';
            self.create_select();
        } else if (element.is('form')) {
            self.type = 'form';
            self.create_form();
        } else {
            self.type = 'link';
            self.create_link();
        }
    },
    finished: function (o, s, xhr) {
        var self = this,
            jqForm = self.element,
            effect = self.config.effect,
            matched = $('.form-messages, .error', jqForm),
            processed = 0;
        jqForm.removeClass(self.config.classes.submit);
        self.disabled = false;
        matched.hide(effect.name, effect.options, effect.speed, function () {
            processed += 1;
            $(this).html('').show();
            if (processed === matched.length) {
                $.djpcms.jsonCallBack(o, s, jqForm);
            }
        });
    },
    form_data: function () {
        var elem = this.element,
            form = elem.closest('form'),
            data = {
                conf: elem.data('warning'),
                name: elem.attr('name'),
                url: elem.attr('href') || elem.data('href'),
                type: elem.data('method') || 'get',
                submit: elem.data('submit')
            };
        if (form.length === 1) {
            data.form = form;
        }
        if (!data.url && data.form) {
            data.url = data.form.attr('action');
        }
        if (!data.url) {
            data.url = window.location.toString();
        }
        return data;
    },
    // Submit data via ajax
    submit: function (data) {
        var self = this;
        //
        function loader(ok) {
            if (ok) {
                var submit_data = $.djpcms.ajaxparams(data.name, data.submit),
                    opts = {
                        url: data.url,
                        type: data.type,
                        dataType: self.config.dataType,
                        data: submit_data
                    };
                self.info('Submitting ajax ' + opts.type + ' request "' + data.name + '"');
                if (!data.form) {
                    opts.data.value = self.element.val();
                    opts.success = $.djpcms.jsonCallBack;
                    $.ajax(opts);
                } else {
                    $.extend(opts, self.config.form);
                    //data.form[0].clk = self.element[0];
                    data.form.ajaxSubmit(opts);
                }
            }
        }
        if (data.conf) {
            $.djpcms.warning_dialog(data.conf.title || '', data.conf.body || data.conf, loader);
        } else {
            loader(true);
        }
    },
    create_select: function () {
        var self = this,
            data = self.form_data();
        self.element.change(function (event) {
            self.submit(data);
        });
    },
    create_link: function () {
        var self = this,
            data = self.form_data();
        self.element.click(function (event) {
            event.preventDefault();
            self.submit(data);
        });
    },
    create_form: function () {
        var self = this,
            form = self.element,
            opts = {
                url: form.attr('action'),
                type: form.attr('method'),
                dataType: self.config.dataType
            },
            name;
        $.extend(opts, self.config.form);
        form.ajaxForm(opts);
        if (form.hasClass(self.config.classes.autoload)) {
            name = form.attr("name");
            form[0].clk = $(":submit[name='" + name + "']", form)[0];
            form.submit();
        }
    }
});