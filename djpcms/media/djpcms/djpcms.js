/* Description:  djpcms Javascript Site Manager
 * Author:       Luca Sbardella
 * Language:     Javascript
 * License:      new BSD licence
 * Contact:      luca.sbardella@gmail.com
 * web:          https://github.com/lsbardel/djpcms
 * @requires:    jQuery
 *
 * Copyright (c) 2009-2012, Luca Sbardella
 * New BSD License
 * http://www.opensource.org/licenses/bsd-license.php
 *
 */
/*globals window, document, jQuery, console*/
/*jslint nomen: true, plusplus: true */
/**
 *
 * djpcms site handle.
 *
 * It fires two events on the container it is built on.
 *
 * "djpcms-before-loading" just before loading
 * "djpcms-after-loading" just after loading
 *
 * Usage on the main page
 *
 * $(document).djpcms();
 */
(function ($) {
    "use strict";
    /**
     * Common Ancestor jQuery plugin
     */
    $.fn.commonAncestor = function () {
        if (!this.length) {
            return $([]);
        }
        var parents = [],
            minlen = Infinity,
            i,
            j,
            p,
            equal;
        //
        this.each(function () {
            var curparents = $(this).parents();
            parents.push(curparents);
            minlen = Math.min(minlen, curparents.length);
        });
        //
        $.each(parents, function (i, p) {
            parents[i] = p.slice(p.length - minlen);
        });
        // Iterate until equality is found
        for (i = 0; i < parents[0].length; i++) {
            p = parents[0][i];
            equal = true;
            for (j = 1; j < parents.length; j++) {
                if (parents[j][i] !== p) {
                    equal = false;
                    break;
                }
            }
            if (equal) {
                return $(p);
            }
        }
        return $([]);
    };
    /**
     * Logging module for djpcms. Usage
     *
     * var logger = $.logging.getLogger();
     * logger.info('bla')
     */
    $.logging = (function () {
        var levelNames = {},
            logging = {
                loggers: {},
                mapping: {},
                names: {},
                format_error: function (msg, e) {
                    if (e !== undefined) {
                        msg += "- File " + e.fileName + " - Line " + e.lineNumber + ": " + e;
                    }
                    return msg;
                },
                debug: 10,
                info: 20,
                warn: 30,
                error: 40,
                critical: 50,
                logclass: 'log'
            };
        // Logging levels
        logging.levels = {
            debug: {
                level: logging.debug,
                name: 'DEBUG'
            },
            info: {
                level: logging.info,
                name: 'INFO'
            },
            warn: {
                level: logging.warn,
                name: 'WARN'
            },
            error: {
                level: logging.error,
                name: 'ERROR',
                f: function (msg, e) {
                    return logging.format_error(msg, e);
                }
            },
            critical: {
                level: logging.critical,
                name: 'CRITICAL',
                f: function (msg, e) {
                    return logging.format_error(msg, e);
                }
            }
        };
        // Create the mapping between level number and level name
        $.each(logging.levels, function (name, level) {
            levelNames[level.level] = level;
        });
        logging.getLevelName = function (level) {
            var l = levelNames[level];
            if (l !== undefined) {
                l = l.name;
            } else {
                l = 'Level-' + level;
            }
            return l;
        };
        // Default formatter
        logging.default_formatter = function (msg, lvl) {
            var mlevel = logging.getLevelName(lvl),
                dte = new Date(),
                hours = dte.getHours(),
                minutes = dte.getMinutes(),
                seconds = dte.getSeconds();
            if (hours < 10) {hours = '0' + hours; }
            if (minutes < 10) {minutes = '0' + minutes; }
            if (seconds < 10) {seconds = '0' + seconds; }
            return hours + ':' + minutes + ':' + seconds + ' - ' + mlevel + ' - ' + msg;
        };
        // HTML formatter
        logging.html_formatter = function (msg, lvl) {
            var mlevel = logging.getLevelName(lvl);
            msg = logging.default_formatter(msg, lvl);
            return '<pre class="' + logging.logclass + ' ' + mlevel.toLowerCase() + '">' + msg + '</pre>';
        };
        // Get a logger handle
        logging.getLogger = function (name) {
            var logclass = 'log',
                level = 10,
                handlers = [],
                logger;
            if (name === undefined) {
                name = 'root';
            }
            logger = logging.loggers[name];
            if (logger !== undefined) {
                return logger;
            }
            logger = {
                'name': name,
                'level': function () {
                    return level;
                },
                'set_level': function (lev) {
                    level = parseInt(String(lev), 10);
                },
                'addHandler': function (h) {
                    if (h !== undefined) {
                        if (h.formatter === undefined) {
                            h = {'formatter': logging.default_formatter,
                                 'log': h};
                        }
                        handlers.push(h);
                    }
                },
                'log': function (message, lvl) {
                    if (lvl < level) {return; }
                    $.each(handlers, function (i, handle) {
                        handle.log(handle.formatter(message, lvl));
                    });
                }
            };
            // Add console handle
            if (typeof console !== "undefined" && typeof console.log !== "undefined") {
                logger.addHandler(function (msg) {
                    console.log(msg);
                });
            }
            // For each logging level add logging function
            $.each(logging.levels, function (name, level) {
                logger[name] = function (msg, e) {
                    if (level.f) {
                        msg = level.f(msg, e);
                    }
                    logger.log(msg, level.level);
                };
            });
            // Add logger to the global loggers object
            logging.loggers[logger.name] = logger;
            return logger;
        };
        return logging;
    }());
    /**
     *
     * The global djpcms object
     */
    $.djpcms = {
        widgets: {},
        // Base object for widgets
        base_widget: {
            _create: function () {
                return this;
            },
            factory: function () {
                return $.djpcms.widgets[this.name];
            },
            destroy: function () {
                var instances = this.factory().instances,
                    idx = instances.indexOf(this.id),
                    res;
                if (idx !== -1) {
                    res = instances[idx];
                    delete instances[idx];
                    delete res.element[0].djpcms_widget;
                    //res = widgets.instances.splice(idx, 1)[0];
                }
                return res;
            },
            ui: function (name, options_or_element, options) {
                return $.djpcms.ui[name](options_or_element, options);
            },
            tostring: function (msg) {
                if (msg) {
                    msg = this.name + ' ' + this.id + ' - ' + msg;
                } else {
                    msg = this.name + ' ' + this.id;
                }
                return msg;
            },
            debug: function (msg) {$.djpcms.logger.debug(this.tostring(msg)); },
            info: function (msg) {$.djpcms.logger.info(this.tostring(msg)); },
            warn: function (msg) {$.djpcms.logger.warn(this.tostring(msg)); },
            error: function (msg) {$.djpcms.logger.error(this.tostring(msg)); },
            critical: function (msg) {$.djpcms.logger.critical(this.tostring(msg)); }
        },
        // Base object for widget factories.
        widgetmaker: {
            name: 'widget',
            defaultElement: '<div>',
            selector: null,
            instance: function (id) {
                if (typeof id !== 'number') { id = id.id; }
                return this.instances[id];
            },
            options: function () {
                return $.djpcms.options[this.name];
            },
            // Create the widget on element
            create: function (element, options) {
                var maker = this,
                    data = element.data('options'),
                    self,
                    instance_id;
                self = $.extend({}, maker.factory);
                self.id = parseInt(maker.instances.push(self), 10) - 1;
                self.element = element;
                element[0].djpcms_widget = self;
                if (data) {
                    options = $.extend(true, {}, options, data);
                }
                self.config = options;
                $.djpcms.logger.debug('Creating widget ' + self.name);
                self._create();
                return maker.instance(self.id);
            },
            // Given a jQuery object, build as many widgets
            make: function (elements, options) {
                var maker = this,
                    wdgs = [],
                    wdg;
                options = $.extend(true, {}, maker.options(), options);
                $.each(elements, function () {
                    wdg = maker.create($(this), options);
                    if (wdg !== undefined) {
                        wdgs.push(wdg);
                    }
                });
                if (wdgs.length === 1) {
                    wdgs = wdgs[0];
                }
                return wdgs;
            },
            decorate: function (container) {
                var selector = this.selector;
                if (selector) {
                    if (container.is(selector)) {
                        this.make(container);
                    }
                    this.make($(selector, container));
                }
            },
            ui: function (options_or_element, options) {
                var element = options_or_element;
                if (options === undefined && $.isPlainObject(options_or_element)) {
                    options = options_or_element;
                    element = undefined;
                }
                element = $(element || this.defaultElement);
                return this.make(element, options);
            },
            create_ui: function () {
                var self = this;
                return function (options_or_element, options) {
                    return self.ui(options_or_element, options);
                };
            }
        },
        ui: {
            name: 'djpcms',
            widget_head: 'ui-widget-header',
            widget_body: 'ui-widget-content',
            corner_top: 'ui-corner-top',
            corner_bottom: 'ui-corner-bottom',
            ui_input: 'ui-input',
            dialog: function (el, options) {
                var ui = $.djpcms.ui,
                    open = true,
                    wdg;
                options = options || {};
                if (options.autoOpen === false) {
                    open = false;
                }
                options.autoOpen = false;
                wdg = el.dialog(options).dialog('widget');
                if (ui.icons === 'fontawesome') {
                    $('.ui-dialog-titlebar-close', wdg)
                        .html('<i class="icon-remove"></i>')
                        .addClass(ui.classes.float_right);
                }
                if (open) {
                    el.dialog('open');
                }
                return el;
            }
        }
    };
    /**
     * djpcms site manager
     */
    $.djpcms = (function (djpcms) {
        // Private variables
        var actions = {},
            jsonCallBacks = {},
            inrequest = false,
            panel = null,
            appqueue = [],
            logger = $.logging.getLogger(),
            defaults = {
                media_url: "/media/",
                debug: false,
                remove_effect: {type: "drop", duration: 500},
                fadetime: 200
            };
        //
        function widgetmaker(deco, base_widget) {
            var base = base_widget || djpcms.widgetmaker,
                factory = base.factory || djpcms.base_widget;
            deco.factory = $.extend({}, factory, deco);
            deco.superClass = base_widget;
            deco.instances = [];
            $.each(base, function (name, value) {
                if (deco[name] === undefined) {
                    deco[name] = value;
                }
            });
            return deco;
        }
        // Add a new decorator
        function addDecorator(deco) {
            var name = deco.name || djpcms.widgetmaker.name,
                base_widget = djpcms.widgets[name] || djpcms.widgets[djpcms.widgetmaker.name],
                config = deco.config;
            deco.name = name;
            if (config !== undefined) {
                delete deco.config;
            }
            if (defaults[name]) {
                config = $.extend(true, defaults[name], config);
            }
            defaults[name] = config;
            deco = widgetmaker(deco, base_widget);
            djpcms.widgets[name] = deco;
            djpcms.ui[name] = deco.create_ui();
        }
        // Set a logging panel
        function set_logging_pannel(panel) {
            panel = $(panel);
            if (panel.length) {
                logger.addHandler({
                    formatter: $.logging.html_formatter,
                    log: function (msg) {
                        panel.prepend(msg);
                    }
                });
            }
        }
        // Create an object containing data to send to the server via AJAX.
        // *NAME* is the name of the interaction
        function ajaxparams(name, data) {
            var p = {'xhr': name};
            if (data) {
                p = $.extend(p, data);
            }
            return p;
        }
        //
        function queue_application(app) {
            if ($.data(document, 'djpcms')) {
                app();
            } else {
                appqueue.push(app);
            }
        }
        // Set options
        function setOptions(options) {
            $.extend(true, defaults, options);
        }
        // Add a new callback for JSON data
        function addJsonCallBack(jcb) {
            jsonCallBacks[jcb.id] = jcb;
        }
        // Remove a decorator
        function removeDecorator(rid) {
            if ($.djpcms.widgets.hasOwnMethod(rid)) {
                delete $.djpcms.widgets[rid];
            }
        }
        //
        function _jsonParse(data, elem) {
            var id  = data.header,
                jcb = jsonCallBacks[id];
            if (jcb) {
                jcb = jcb.handle(data.body, elem, defaults) && data.error;
            } else {
                logger.error('Could not find callback ' + id);
            }
            return jcb;
        }
        // Add new action
        function addAction(id, action) {
            var a = actions[id];
            if (!a) {
                a = {'action': action, 'ids': {}};
                actions[id] = a;
            } else if (action) {
                a.action = action;
            }
            return a;
        }
        //
        function registerActionElement(actionid, id) {
            var action = addAction(actionid, null);
            action.ids[id] = id;
        }
        //
        function getAction(actionid, id) {
            var action = addAction(actionid, null);
            if (action.ids[id]) {
                delete action.ids[id];
                return action.action;
            }
        }
        /**
         * Handle a JSON call back by looping through all the callback
         * objects registered
         * @param data JSON object already unserialized
         * @param status String status flag
         * @param elem (Optional) jQuery object or HTMLObject
         */
        function _jsonCallBack(data, status, elem) {
            var v = false;
            if (status === "success") {
                v = _jsonParse(data, elem);
            }
            inrequest = false;
            return v;
        }
        /**
         * DJPCMS Handler constructor
         * It applys djpcms decorator to the element.
         */
        function _construct() {
            return this.each(function () {
                var me = $(this),
                    config = defaults,
                    lp = $('.djp-logging-panel', me),
                    //parent = me.closest('.djpcms-loaded'),
                    parent = [];
                //
                if (!parent.length) {
                    if (this === document) {
                        me = $('body');
                    }
                    me.addClass('djpcms-loaded').trigger('djpcms-before-loading');
                    if (lp) {
                        set_logging_pannel(lp);
                    }
                    $.each($.djpcms.widgets, function (name, widget) {
                        widget.decorate(me);
                    });
                    if (this === document) {
                        $.data(this, 'djpcms', config);
                        $.each(appqueue, function (i, app) {
                            app();
                        });
                        appqueue = [];
                    }
                    me.trigger('djpcms-after-loading');
                }
            });
        }
        //
        return $.extend(djpcms, {
            'construct': _construct,
            'options': defaults,
            'jsonParse': _jsonParse,
            'addJsonCallBack': addJsonCallBack,
            'jsonCallBack': _jsonCallBack,
            'decorator': addDecorator,
            'set_options': setOptions,
            'ajaxparams': ajaxparams,
            'set_inrequest': function (v) {inrequest = v; },
            'before_form_submit': [],
            'addAction': addAction,
            'registerActionElement': registerActionElement,
            'getAction': getAction,
            'inrequest': function () {return inrequest; },
            'logger': logger,
            'queue': queue_application,
            'panel': function () {
                // A floating panel
                if (!panel) {
                    panel = $('<div>').hide().appendTo($('body'))
                                    .addClass('float-panel ui-widget ui-widget-content ui-corner-all')
                                    .css({position: 'absolute',
                                         'text-align': 'left',
                                          padding: '5px'});
                }
                return panel;
            },
            'smartwidth': function (html) {
                return Math.max(15 * Math.sqrt(html.length), 200);
            }
        });
    }($.djpcms));
    //
    // extend plugin scope
    $.fn.extend({
        djpcms: $.djpcms.construct
    });
    //
    $.djpcms.confirmation_dialog = function (title, html, callback, opts) {
        var el = $('<div title="' + title + '"></div>').html(String(html)),
            options = $.extend({}, opts, {
                modal: true,
                draggable: false,
                resizable: false,
                buttons: {
                    Ok: function () {
                        $(this).dialog("close");
                        callback(true);
                    },
                    Cancel: function () {
                        $(this).dialog("close");
                        callback(false);
                    }
                },
                close: function (event, ui) {
                    el.dialog('destroy').remove();
                }
            });
        return $.djpcms.ui.dialog(el, options);
    };
    // Warning dialog
    $.djpcms.warning_dialog = function (title, warn, callback) {
        var opts = {
                dialogClass: 'ui-state-error',
                autoOpen: false
            },
            el = $.djpcms.confirmation_dialog(title, warn, callback, opts);
        $('.ui-dialog-titlebar, .ui-dialog-buttonpane', el.dialog('widget'))
                    .addClass('ui-state-error');
        el.dialog("open");
        return el;
    };
    /**
     *  DJPCMS AJAX DATA LOADER CLOSURE.
     *
     *  An utility which return a function which can be used to
     *  perform AJAX requests with confirmation and callbacks handled
     *  by djpcms callbacks.
     *
     *  For example
     *
     *  myloader = $.djpcms.ajax_loader('/my/path/','reload','post')
     *  myloader()
     *
     */
    $.djpcms.ajax_loader =  function djpcms_loader(url, action, method, data, conf) {
        var sendrequest = function (callback) {
            var that = this;
            if (conf && !callback) {
                $('<div></div>').html(conf).dialog({
                    modal: true,
                    draggable: false,
                    resizable: false,
                    buttons: {
                        Ok: function () {
                            $(this).dialog("close");
                            sendrequest(true);
                        },
                        Cancel: function () {
                            $(this).dialog("close");
                            $.djpcms.set_inrequest(false);
                        }
                    }
                });
            } else {
                $.ajax({
                    'url': url,
                    'type': method || 'post',
                    'dataType': 'json',
                    'success': function (e, s) {
                        $.djpcms.set_inrequest(false);
                        $.djpcms.jsonCallBack(e, s, that);
                    },
                    'data': $.djpcms.ajaxparams(action, data)
                });
            }
        };
        return sendrequest;
    };
    //
    $.djpcms.ajax_loader_from_tool = function (tool) {
        if (tool.ajax) {
            return $.djpcms.ajax_loader(tool.url,
                                        tool.action,
                                        tool.method,
                                        tool.data,
                                        tool.conf);
        }
    };
    /**
     * A modal error dialog
     */
    $.djpcms.errorDialog = function (html, title) {
        title = title || 'Something did not work';
        var el = $('<div title="' + title + '"></div>').html(String(html)),
            width = $.djpcms.smartwidth(html);
        el.dialog({modal: true,
                   autoOpen: false,
                   dialogClass: 'ui-state-error',
                   'width': width});
        $('.ui-dialog-titlebar', el.dialog('widget')).addClass('ui-state-error');
        el.dialog("open");
    };
    /**
     *
     * JSON CALLBACKS
     */
    $.djpcms.addJsonCallBack({
        id: "error",
        handle: function (data, elem) {
            $.djpcms.errorDialog(data);
        }
    });
    //
    $.djpcms.addJsonCallBack({
        id: "servererror",
        handle: function (data, elem) {
            $.djpcms.errorDialog(data, "Unhandled Server Error");
        }
    });
    //
    $.djpcms.addJsonCallBack({
        id: "message",
        handle: function (data, elem) {
            $.djpcms.logger.info(data);
            return true;
        }
    });
    //
    $.djpcms.addJsonCallBack({
        id: "empty",
        handle: function (data, elem) {
            return true;
        }
    });
    /**
     * collection callback
     */
    $.djpcms.addJsonCallBack({
        id: "collection",
        handle: function (data, elem) {
            $.each(data, function (i, component) {
                $.djpcms.jsonParse(component, elem);
            });
            return true;
        }
    });
    /**
     * html JSON callback. The server returns a list of objects with
     * a selctor and html attributes which are going to be
     * added/replaced to the document
     */
    $.djpcms.addJsonCallBack({
        id: "htmls",
        handle: function (data, elem, config) {
            $.each(data, function (i, b) {
                var el = $(b.identifier, elem),
                    fade = config.fadetime,
                    html;
                if (!el.length && b.alldocument) {
                    el = $(b.identifier);
                }
                if (el.length) {
                    if (b.type === 'hide') {
                        el.hide();
                    } else if (b.type === 'show') {
                        el.show();
                    } else if (b.type === 'value') {
                        el.val(b.html);
                    } else if (b.type === 'append') {
                        $(b.html).djpcms().appendTo(el);
                    } else {
                        html = $(b.html).djpcms();
                        el.show();
                        el.fadeOut(fade, 'linear', function () {
                            if (b.type === 'replacewith') {
                                el.replaceWith(html);
                            } else {
                                if (b.type === 'addto') {
                                    el.append(html);
                                } else {
                                    // The append method does not seems to
                                    // presenve events on html. So I use this
                                    // hack.
                                    var tmp = $('<div></div>');
                                    el.empty().append(tmp);
                                    tmp.replaceWith(html);
                                }
                            }
                            el.fadeIn(fade);
                        });
                    }
                }
            });
            return true;
        }
    });
    /**
     * attribute JSON callback
     */
    $.djpcms.addJsonCallBack({
        id: "attribute",
        handle: function (data, elem) {
            var selected = [];
            $.each(data, function (i, b) {
                var el;
                if (b.alldocument) {
                    el = $(b.selector);
                } else {
                    el = $(b.selector, elem);
                }
                if (el.length) {
                    b.elem = el;
                }
            });
            $.each(data, function (i, b) {
                if (b.elem) {
                    b.elem.attr(b.attr, b.value);
                }
            });
        }
    });
    /**
     * Remove html elements
     */
    $.djpcms.addJsonCallBack({
        id: "remove",
        handle: function (data, elem) {
            $.each(data, function (i, b) {
                var el = $(b.identifier, elem),
                    be = $.djpcms.options.remove_effect;
                if (!el.length && b.alldocument) {
                    el = $(b.identifier);
                }
                if (el.length) {
                    el.fadeIn(be.duration, function () {el.remove(); });
                    //el.hide(be.type,{},be.duration,function() {el.remove();});
                }
            });
            return true;
        }
    });
    /**
     * Redirect
     */
    $.djpcms.addJsonCallBack({
        id: "redirect",
        handle: function (data, elem) {
            window.location = data;
        }
    });
    /**
     * Dialog callback
     *
     * Create a jQuery dialog from JSON data
     */
    $.djpcms.addJsonCallBack({
        id: "dialog",
        handle: function (data, elem) {
            var el = $('<div></div>').html(data.html).djpcms(),
                buttons = {},
                options = data.options;
            $.each(data.buttons, function (n, b) {
                buttons[b.name] = function () {
                    b.d = $(this);
                    b.dialogcallBack = function (data) {
                        $.djpcms.jsonCallBack(data, 'success', el);
                        if (b.close) {
                            b.d.dialog("close");
                        }
                    };
                    if (b.url) {
                        var params = $('form', el).formToArray(),
                            extra;
                        if (b.func) {
                            extra = $.djpcms.ajaxparams(b.func);
                            $.each(extra, function (k, v) {
                                params.push({'name': k, 'value': v});
                            });
                        }
                        $.post(b.url,
                                $.param(params),
                                b.dialogcallBack,
                                "json");
                    } else {
                        b.d.dialog('close');
                    }
                };
            });
            options.buttons = buttons;
            el.dialog(options);
            return true;
        }
    });
    ////////////////////////////////////////////////////////////////////////////
    //                    WIDGETS - DECORATORS
    ////////////////////////////////////////////////////////////////////////////
    /**
     * BASE WIDGET
     */
    $.djpcms.decorator({
        config: {
            classes: {
                widget: 'ui-widget',
                head: 'ui-widget-header',
                body: 'ui-widget-content',
                foot: 'ui-widget-footer',
                active: 'ui-state-active',
                clickable: 'ui-clickable',
                float_right: 'f-right'
            }
        }
    });
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
            form: {
                iframe: false,
                beforeSerialize: function (jqForm, opts) {
                    return true;
                },
                beforeSubmit: function (formData, jqForm, opts) {
                    var self = jqForm[0].djpcms_widget;
                    $.each($.djpcms.before_form_submit, function () {
                        formData = this(formData, jqForm);
                    });
                    jqForm.addClass(self.config.classes.submit);
                    return true;
                },
                success: function (o, s, xhr, jqForm) {
                    var self = jqForm[0].djpcms_widget;
                    jqForm.removeClass(self.config.classes.submit);
                    $.djpcms.jsonCallBack(o, s, jqForm);
                },
                error: function (o, s, xhr, jqForm) {
                    var self = jqForm[0].djpcms_widget;
                    jqForm.removeClass(self.config.classes.submit);
                    $.djpcms.jsonCallBack(o, s, jqForm);
                }
            },
            timeout: 30
        },
        _create: function () {
            var self = this,
                element = self.element;
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
        form_data: function () {
            var elem = this.element,
                form = elem.closest('form'),
                data = {
                    conf: elem.data('warning'),
                    name: elem.attr('name'),
                    url: elem.attr('href') || elem.data('href'),
                    type: elem.data('method') || 'get'
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
        submit: function (data) {
            var self = this;
            //
            function loader(ok) {
                if (ok) {
                    var opts = {
                            url: data.url,
                            type: data.type,
                            dataType: self.config.dataType,
                            data: $.djpcms.ajaxparams(data.name)
                        };
                    self.info('Submitting ajax ' + opts.type +' request "' + data.name + '"');
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
    /**
     * Autocomplete Off
     */
    $.djpcms.decorator({
        name: "autocomplete_off",
        decorate: function ($this) {
            $('.autocomplete-off', $this).each(function () {
                $(this).attr('autocomplete', 'off');
            });
            $('input:password', $this).each(function () {
                $(this).attr('autocomplete', 'off');
            });
        }
    });
    //
    // Calendar Date Picker Decorator
    $.djpcms.decorator({
        name: "datepicker",
        selector: 'input.dateinput',
        config: {
            dateFormat: 'd M yy'
        },
        _create: function () {
            this.element.datepicker(this.config);
        }
    });
    // Currency Input
    $.djpcms.decorator({
        name: "numeric",
        selector: 'input.numeric',
        config: {
            classes: {
                negative: 'negative'
            }
        },
        format: function () {
            var elem = this.element,
                nc = this.config.classes.negative,
                v = $.djpcms.format_currency(elem.val());
            if (v.negative) {
                elem.addClass(nc);
            } else {
                elem.removeClass(nc);
            }
            elem.val(v.value);
        },
        _create: function () {
            var self = this;
            this.element.keyup(function () {
                self.format();
            });
        }
    });
    //
    $.djpcms.decorator({
        name: 'message',
        selector: 'li.messagelist, li.errorlist',
        config: {
            dismiss: true,
            fade: 400,
            float: 'right'
        },
        _create: function () {
            var self = this,
                opts = self.config,
                a = $('<a><span class="ui-icon ui-icon-closethick"></span></a>')
                    .css({'float': opts.float})
                    .addClass('ui-corner-all')
                    .mouseenter(function () {$(this).addClass('ui-state-hover'); })
                    .mouseleave(function () {$(this).removeClass('ui-state-hover'); })
                    .click(function () {
                        $(this).parent('li').fadeOut(opts.fade, 'linear', function () {
                            $(this).remove();
                        });
                    });
            self.element.append(a);
        }
    });
    /**
     * Format a number and return a string based on input settings
     * @param {Number} number The input number to format
     * @param {Number} decimals The amount of decimals
     * @param {String} decPoint The decimal point, defaults to the one given in the lang options
     * @param {String} thousandsSep The thousands separator, defaults to the one given in the lang options
     */
    //$.djpcms.numberFormat = function (number, decimals, decPoint, thousandsSep) {
    //    var lang = defaultOptions.lang,
    //        // http://kevin.vanzonneveld.net/techblog/article/javascript_equivalent_for_phps_number_format/
    //        n = number, c = isNaN(decimals = mathAbs(decimals)) ? 2 : decimals,
    //        d = decPoint === undefined ? lang.decimalPoint : decPoint,
    //        t = thousandsSep === undefined ? lang.thousandsSep : thousandsSep, s = n < 0 ? "-" : "",
    //        i = String(pInt(n = mathAbs(+n || 0).toFixed(c))),
    //        j = i.length > 3 ? i.length % 3 : 0;
    //
    //    return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) +
    //        (c ? d + mathAbs(n - i).toFixed(c).slice(2) : "");
    //};
    /**
     * Return an object containing the formatted currency and a flag
     * indicating if it is negative
     */
    $.djpcms.format_currency = function (s, precision) {
        if (!precision) {
            precision = 3;
        }
        s = s.replace(/,/g,'');
        var c = parseFloat(s),
            isneg = false,
            decimal = false,
            de = '',
            i,
            cs,
            cn,
            d,
            k,
            N,
            mul,
            atom;
        //
        if (isNaN(c)) {
            cs = s;
        } else {
            cs = s.split('.', 2);
            if (c < 0) {
                isneg = true;
                c = Math.abs(c);
            }
            cn = parseInt(c, 10);
            if (cs.length === 2) {
                de = cs[1];
                if (!de) {
                    de = '.';
                } else {
                    decimal = true;
                    de = c - cn;
                }
            }
            if (decimal) {
                mul = Math.pow(10, precision);
                atom = String(parseInt(c * mul, 10) / mul).split(".")[1];
                de = '';
                decimal = false;
                for (i = 0; i < Math.min(atom.length, precision); i++) {
                    de += atom[i];
                    if (parseInt(atom[i], 10) > 0) {
                        decimal = true;
                    }
                }
                if (decimal) {
                    de = '.' + de;
                }
            }
            cn += "";
            N  = cn.length;
            cs = "";
            for (i = 0; i < N; i++) {
                cs += cn[i];
                k = N - i - 1;
                d = parseInt(k / 3, 10);
                if (3 * d === k && k > 0) {
                    cs += ',';
                }
            }
            cs += de;
            if (isneg) {
                cs = '-' + cs;
            } else {
                cs = String(cs);
            }
        }
        return {
            value: cs,
            negative: isneg
        };
    };
}(jQuery));