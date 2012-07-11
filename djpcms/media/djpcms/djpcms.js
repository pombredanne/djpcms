/* Description:  djpcms Javascript Site Manager
 * Author:       Luca Sbardella
 * Language:     Javascript
 * License:      new BSD licence
 * Contact:      luca.sbardella@gmail.com
 * web:          https://github.com/lsbardel/djpcms
 * @requires:    jQuery, jQuery-UI
 * 
 * Copyright (c) 2009-2011, Luca Sbardella
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
            i, j, p, equal;
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
                return l.name;
            } else {
                return 'Level-' + level;
            }
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
    
    $.djpcms = {
        base_widget: {
            name: 'widget',
            as_widget: true,
            defaultElement: '<div>',
            selector: null,
            config: {},
            decorate: function (container) {
                var selector = this.selector;
                if (selector) {
                    this.make($(selector, container));
                }
            },
            _create: function() {
                return this;
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
        var widgets = {},
            instances = [],
            actions = {},
            jsonCallBacks = {},
            logging_pannel = null,
            inrequest = false,
            panel = null,
            appqueue = [],
            logger = $.logging.getLogger(),
            defaults = {
                media_url: "/media/",
                classes: {
                    active: 'ui-state-active',
                    clickable: 'ui-clickable',
                    float_right: 'f-right',
                },
                ajax_server_error: "ajax-server-error",
                errorlist: "errorlist",
                formmessages: "form-messages",
                remove_effect: {type: "drop", duration: 500},
                fadetime: 200,
                debug: false
            };            
        // Add a new decorator
        function addDecorator(deco) {
            var widget = $.extend({'djpcms': djpcms}, djpcms.base_widget, deco),
                name = widget.name,
                factory = $.extend({destroy: function () {
                    var idx = widgets.instances.indexOf(this.id),
                        res;
                    if(idx !== -1) {
                        res = widgets.instances[idx];
                        delete widgets.instances[idx];
                        //res = widgets.instances.splice(idx, 1)[0];
                    }
                    return res;
                }}, widget);
            defaults[name] = widget.config;
            widgets[name] = widget;
            delete widget.config;
            // Create the widget factory
            $.extend(widget, {
                'factory': factory,
                instances: [],
                instance: function (id) {
                    if (typeof id !== 'number') { id = id.id; }
                    return this.instances[id];
                },
                // Create the widget on element
                create: function (element, options) {
                    var widget = this,
                        element = $(element),
                        data = element.data('options'),
                        self, instance_id;
                    if (!options) {
                        options = $.extend({}, widget.options(), data);
                    } else {
                        options = $.extend({}, widget.options(), data, options);
                    }
                    self = $.extend({}, widget.factory),
                    self.id = parseInt(widget.instances.push(self), 10) - 1;
                    self.element = element;
                    self.config = options;
                    djpcms.logger.debug('Creating widget ' + widget.name);
                    self._create();
                    return this.instance(self.id);
                },
                // Given a jQuery object, build as many widgets
                make: function (elements, options) {
                    var self = this,
                        wdgs = [],
                        wdg;
                    $.each(elements, function() {
                        wdg = widget.create(this, options);
                        if (wdg !== undefined) {
                            wdgs.push(wdg);
                        }
                    });
                    if(wdgs.length === 1) {
                        wdgs = wdgs[0];
                    }
                    return wdgs;
                }
            });
            // Add options function
            widget.options = function () {
                return djpcms.options[widget.name];
            }
            // The user interface factory
            djpcms.ui[name] = function (options_or_element, options) {
                var element = options_or_element;
                if (options === undefined && $.isPlainObject(options_or_element)) {
                    options = options_or_element;
                    element = undefined;
                }
                element = $(element || widget.defaultElement);
                return widget.make(element, options);
            };
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
            if (widgets.hasOwnMethod(rid)) {
                delete widgets[rid];
            }
        }
        //
        function _jsonParse(data, elem) {
            var id  = data.header,
                jcb = jsonCallBacks[id];
            if (jcb) {
                return jcb.handle(data.body, elem, defaults) && data.error;
            } else {
                logger.error('Could not find callback ' + id);
            }
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
                    $.each(widgets, function (name, widget) {
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
            construct: _construct,
            options: defaults,
            jsonParse: _jsonParse,
            'addJsonCallBack': addJsonCallBack,
            'jsonCallBack': _jsonCallBack,
            decorator: addDecorator,
            set_options: setOptions,
            'ajaxparams': ajaxparams,
            set_inrequest: function (v) {inrequest = v; },
            before_form_submit: [],
            //
            // Action in slements ids
            'addAction': addAction,
            'registerActionElement': registerActionElement,
            'getAction': getAction,
            //
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
            smartwidth: function (html) {
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
    //
    $.djpcms.addJsonCallBack({
        id: "autocomplete",
        handle: function (data, elem) {
            elem.response($.map(data, function (item) {
                return {
                    value: item[0],
                    label: item[1],
                    real_value: item[2],
                    multiple: elem.multiple
                };
            }));
        }
    });
    ////////////////////////////////////////////////////////////////////////////
    //                      DECORATORS
    ////////////////////////////////////////////////////////////////////////////
    /**
     * Accordion menu
     */
    $.djpcms.decorator({
        name: "accordion",
        selector: '.ui-accordion-container',
        config: {            
            effect: null,//'drop',
            fadetime: 200,
            autoHeight: false,
            fillSpace: false
        },
        _create: function () {
            var element = this.element,
                opts = this.config;
            element.accordion(opts).show(opts.effect, {}, opts.fadetime);
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
        defaultElement: 'a',
        selector: '.ajax',
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
            timeout: 30
        },
        _create: function () {
            var self = this,
                element = self.element,
                config = self.config,
                confirm = config.confirm_actions,
                callback = $.djpcms.jsonCallBack,
                logger = $.djpcms.logger;
            // Links and buttons
            if (element.is('select')) {
                self.type = 'select';
                self.create_select();
            } else if (element.is('form')) {
                self.type = 'form';
                self.create_form();
            } else {
                self.type = 'link';
                self.create_link();
            }
        },
        create_select: function() {
            var self = this,
                config = self.config;
            self.element.change(function (event) {
                var elem = $(this),
                    data = elem.data(),
                    url = data.href,
                    name = elem.attr('name'),
                    form = elem.closest('form'),
                    method = data.method || 'get',
                    opts,
                    p;
                if (form.length === 1 && !url) {
                    url = form.attr('action');
                }
                if (!url) {
                    url = window.location.toString();
                }
                if (!form) {
                    p = $.djpcms.ajaxparams(elem.attr('name'));
                    p.value = elem.val();
                    $.post(url, $.param(p), $.djpcms.jsonCallBack, "json");
                } else {
                    // we are going to use the form submit so we send
                    // all form's inputs too.
                    opts = {
                        'url': url,
                        'type': method,
                        success: callback,
                        dataType: config.dataType,
                        data: {xhr: name},
                        iframe: false
                    };
                    form[0].clk = elem[0];
                    logger.info('Submitting select change from "' + name + '"');
                    form.ajaxSubmit(opts);
                }
            });
        },
        create_link: function () {
            // Handle click
            function handleClick(handle) {
                var url = elem.attr('href') || elem.data('href') || '.',
                    method,
                    action;
                if (!handle) {return; }
                if (!elem.hasClass('ajax')) {
                    window.location = url;
                } else {
                    method = elem.data('method') || 'post';
                    action = elem.attr('name');
                    $.djpcms.ajax_loader(url, action, method, {})();
                }
            }
            this.element.click(function (event) {
                event.preventDefault();
                var elem = $(this),
                    ajax = elem.hasClass('ajax'),
                    conf = elem.data('warning'),
                    form = elem.closest('form');
                if (conf) {
                    $.djpcms.warning_dialog(conf.title || '',
                                            conf.body || conf,
                                            handleClick);
                } else {
                    handleClick(true);
                }
            });
        },
        form_beforeSerialize: function (jqForm, opts) {
            return true;
        },
        form_beforeSubmit: function (formData, jqForm, opts) {
            $.each($.djpcms.before_form_submit, function () {
                formData = this(formData, jqForm);
            });
            jqForm.addClass(self.config.classes.submit);
            return true;
        },
        form_success: function (o, s, xhr, jqForm) {
            jqForm.removeClass(self.config.classes.submit);
            $.djpcms.jsonCallBack(o, s, jqForm);
        },
        create_form: function() {
            var self = this,
                f = self.element,
                opts = {
                    url: f.attr('action'),
                    type: f.attr('method'),
                    success: self.form_success,
                    dataType: self.config.dataType,
                    beforeSerialize: self.form_beforeSerialize,
                    beforeSubmit: self.form_beforeSubmit,
                    iframe: false
                },
                name;
            f.ajaxForm(opts);
            if (f.hasClass(self.config.classes.autoload)) {
                name = f.attr("name");
                f[0].clk = $(":submit[name='" + name + "']", f)[0];
                f.submit();
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
            this.element.datepicker(self.config);
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
        format: function (elem, nc) {
            var elem = self.element,
                nc = self.config.classes.negative;
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
        name: 'asmSelect',
        selector: 'select[multiple="multiple"]',
        config: {
            addItemTarget: 'bottom',
            animate: true,
            highlight: true,
            sortable: false
        },
        _create: function () {
            self.element.bsmSelect(self.config);
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
                opts = self.config;
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
     * AUTOCOMPLETE
     * 
     * The actual values are stored in the data attribute of the input element.
     * The positioning is with respect the "widgetcontainer" parent element if
     * available.
     */
    $.djpcms.decorator({
        name: "autocomplete",
        description: "Autocomplete to an input",
        defaultElement: 'input',
        selector: 'input.autocomplete',
        config: {
            classes: {
                autocomplete: 'autocomplete',
            },
            widgetcontainer: '.ui-input',
            minLength: 2,
            maxRows: 50,
            search_string: 'q',
            separator: ', '
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
        get_real_data: function  (multiple, separator) {
            return function (val) {
                if (multiple) {
                    var data = [];
                    $.each(clean_data(split(val), this.data), function (i, d) {
                        data.push(d.value);
                    });
                    return data.join(separator);
                } else {
                    if (val && this.data.length) {
                        return this.data[0].real_value;
                    } else {
                        return '';
                    }
                }
            };
        },
        single_add_data: function  (item) {
            this.real.val(item.real_value);
            this.proxy.val(item.value);
            this.real.data('value', item.value);
        },
        multiple_add_data: function (item) {
            var terms = split(this.value);
            terms.pop();
            data = clean_data(terms, data);
            terms.push(display);
            new_data.push(item);
            terms.push("");
            display = terms.join(separator);
            real_data['data'] = data;
        },
        get_autocomplete_data: function (jform, options, veto) {
            var value = this.proxy.val();
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
                opts = self.config;
                elem = this.element,
                name = elem.attr('name'),
                data = elem.data(),
                url = data.url,
                choices = data.choices,
                maxRows = data.maxrows || opts.maxRows,
                search_string = data.search_string || opts.search_string,
                multiple = data.multiple,
                separator = data.separator || opts.separator,
                initials,
                manager = {
                    'name': name,
                    proxy: elem,
                    widget: elem,
                    'multiple': multiple,
                    add_data: multiple ? multiple_add_data : single_add_data
                },
                options = {
                    minLength: data.minlength || opts.minLength,
                    select: function (event, ui) {
                        manager.add_data(ui.item);
                        return false;
                    }
                };
            // Bind to form pre-serialize 
            elem.closest('form').bind('form-pre-serialize', $.proxy(get_autocomplete_data, manager));
            // Optain the widget container for positioning if specified. 
            if (opts.widgetcontainer) {
                manager.widget = elem.parent(opts.widgetcontainer);
                if (!manager.widget.length) {
                    manager.widget = elem;
                }
                options.position = {of: manager.widget};
            }
            // Build the real (hidden) input
            if(multiple) {
                manager.real = $('<select name="'+ name +'[]" multiple="multiple"></select>');
            } else {
                manager.real = $('<input name="'+ name +'"></input>');
            }
            elem.attr('name',name+'_proxy');
            manager.widget.prepend(manager.real.hide());
            //
            if(multiple) {
                options.focus = function() {
                    return false;
                };
                elem.bind("keydown", function( event ) {
                    if ( event.keyCode === $.ui.keyCode.TAB &&
                            $( this ).data( "autocomplete" ).menu.active ) {
                        event.preventDefault();
                    }
                });
            }
            initials = data.initial_value;
            if(initials) {
                $.each(initials, function(i,initial) {
                    manager.add_data({real_value: initial[0],
                                      value: initial[1]});
                });
            }
            
            // If choices are available, it is a locfal autocomplete.
            if(choices && choices.length) {
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
            }
            else if(url) {
                // We have a url, the data is obtained remotely.
                options.source = function(request,response) {
                                var ajax_data = {style: 'full',
                                                 maxRows: maxRows,
                                                 'search_string': search_string 
                                                 };
                                ajax_data[search_string] = request.term;
                                var loader = $.djpcms.ajax_loader(url,
                                                                'autocomplete',
                                                                'get',ajax_data),
                                    that = {'response':response,
                                            'multiple': multiple,
                                            'request':request};                                    
                                $.proxy(loader,that)();
                            };
                elem.autocomplete(options);
            }
        }
    });
    /**
     * Page blocks rearranging
     */
    $.djpcms.decorator({
        name: "rearrange",
        selector: 'body.editable',
        config: {
            cmsblock: '.cms-edit-block',
            placeholder: 'cms-block-placeholder',
            cmsform: 'form.cms-blockcontent',
            movable: '.movable',
            sortblock: '.sortable-block'
        },
        description: "Drag and drop functionalities in editing mode",
        _create: function() {
            var options = this.config;
            if(!$.djpcms.content_edit) {
                return;
            }
            // Decorate
            $.djpcms.content_edit = (function() {
                var movable = options.movable,
                    cmsblock = options.cmsblock,
                    sortblock = options.sortblock,
                    columns = $(sortblock),
                    holderelem = columns.commonAncestor(),
                    curposition = null,
                    logger = $.djpcms.logger;
                
                
                columns.delegate(cmsblock+movable+' .hd', 'mousedown', function(event) {
                    var block = $(this).parent(movable);
                    if(block.length) {
                        curposition = position(block);
                    }
                });
                
                function position(elem) {
                    var neighbour = elem.prev(cmsblock),
                        data = {};
                    if(neighbour.length) {
                        data.previous = neighbour.attr('id');
                    }
                    else {
                        neighbour = elem.next(cmsblock);
                        if(neighbour.length) {
                            data.next = neighbour.attr('id');
                        }
                    }
                    return data;
                }
                
                function moveblock(elem, pos, callback) {
                    var form = $(options.cmsform, elem);
                    if(form) {
                        var data = $.extend($.djpcms.ajaxparams('rearrange'), pos),
                            url = form.attr('action');
                        logger.info('Updating position at "'+url+'"');
                        $.post(url, data, callback, 'json');
                    }
                }
            
                columns.sortable({
                    items: cmsblock,
                    cancel: cmsblock+ ":not("+movable+")",
                    handle: '.hd',
                    forcePlaceholderSize: true,
                    connectWith: sortblock,
                    revert: 300,
                    delay: 100,
                    opacity: 0.8,
                    //containment: holderelem,
                    placeholder: options.placeholder,
                    start: function (e, ui) {
                        var block = ui.item.addClass('dragging');
                        $.djpcms.logger.info('Moving '+block.attr('id'));
                        block.width(block.width());
                    },
                    stop: function (e, ui) {
                        var elem = ui.item,
                            pos = position(elem);
                        logger.info('Stopping ' + elem.attr('id'));
                        elem.css({width:''}).removeClass('dragging');
                        if(pos.previous) {
                            if(pos.previous === curposition.previous) {return;}
                        }
                        else {
                            if(pos.next === curposition.next) {return;}
                        }
                        columns.sortable('disable');
                        moveblock(elem, pos, function (e, s) {
                            columns.sortable('enable');
                            $.djpcms.jsonCallBack(e, s);
                        });
                    }
                });
            }());
        }
    });
    //
    $.djpcms.decorator({
        name: "textselect",
        selector: 'select.text-select',
        description: "A selct widget with text to display",
        _create: function() {
            var elems = $(config.textselect.selector,$this);
            
            // The selectors
            function text(elem) {
                var me = $(elem),
                    val = me.val(),
                    target = me.data('target');
                if(target) {
                    $('.target',target).hide();
                    if(val) {
                        $('.target.'+val,target).show();
                    }
                }
            }
            
            $.each(elems,function() {
                var me = $(this),
                    target = me.data('target');
                if(target) {
                    var t = $(target,$this);
                    if(!t.length) {
                        t = $(target)
                    }
                    if(t.length) {
                        me.data('target',t);
                        text(me);
                    }
                    else {
                        me.data('target',null);
                    }
                }
            });
            elems.change(function(){text(this)});
        }
    });
    //
    $.djpcms.decorator({
        name: "popover",
        selector: '.pop-over, .label',
        config: {
            x:10,
            y:30,
            predelay: 400,
            effect:'fade',
            fadeOutSpeed:200,
            position: "top"
        },
        _create: function () {
            if ($.fn.popover) {
                var self = this,
                    el = self.element,
                    des = el.data('content');
                if(des) {
                    el.attr('rel','popover');
                    el.popover();
                }
            } else {
                self.destroy();
            }
        }
    }); 
    /**
     * Format a number and return a string based on input settings
     * @param {Number} number The input number to format
     * @param {Number} decimals The amount of decimals
     * @param {String} decPoint The decimal point, defaults to the one given in the lang options
     * @param {String} thousandsSep The thousands separator, defaults to the one given in the lang options
     */
    $.djpcms.numberFormat = function (number, decimals, decPoint, thousandsSep) {
        var lang = defaultOptions.lang,
            // http://kevin.vanzonneveld.net/techblog/article/javascript_equivalent_for_phps_number_format/
            n = number, c = isNaN(decimals = mathAbs(decimals)) ? 2 : decimals,
            d = decPoint === undefined ? lang.decimalPoint : decPoint,
            t = thousandsSep === undefined ? lang.thousandsSep : thousandsSep, s = n < 0 ? "-" : "",
            i = String(pInt(n = mathAbs(+n || 0).toFixed(c))),
            j = i.length > 3 ? i.length % 3 : 0;
        
        return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) +
            (c ? d + mathAbs(n - i).toFixed(c).slice(2) : "");
    };
    /**
     * Return an object containing the formatted currency and a flag
     * indicating if it is negative
     */
    $.djpcms.format_currency = function(s,precision) {
        if(!precision) {
            precision = 3;
        }
        s = s.replace(/,/g,'');
        var c = parseFloat(s),
            isneg = false,
            decimal = false,
            cs,cn,d,k,N,de = '';
        if(isNaN(c))  {
            return {value:s,negative:isneg};
        }
        cs = s.split('.',2);
        if(c<0) {
            isneg = true;
            c = Math.abs(c);
        }
        cn = parseInt(c,10);
        if(cs.length == 2) {
            de = cs[1];
            if(!de) {
                de = '.';
            } else {
                decimal = true;
                de = c - cn;
            }
        }
        if(decimal) {
            var mul = Math.pow(10,precision);
            var atom = (parseInt(c*mul)/mul + '').split(".")[1];
            var de = '';
            decimal = false;
            for(var i=0;i<Math.min(atom.length,precision);i++)  {
                de += atom[i];
                if(parseInt(atom[i],10) > 0)  {
                    decimal = true;
                }
            }
            if(decimal) {de = '.' + de;}
        }
        cn += "";
        N  = cn.length;
        cs = "";
        for(var j=0;j<N;j++)  {
            cs += cn[j];
            k = N - j - 1;
            d = parseInt(k/3,10);
            if(3*d == k && k > 0) {
                cs += ',';
            }
        }
        cs += de;
        if(isneg) {
            cs = '-'+cs;
        }
        else {
            cs = ''+cs;
        }
        return {value:cs,negative:isneg};
    };
}(jQuery));