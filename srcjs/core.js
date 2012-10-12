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
        if (console !== undefined && console.log !== undefined) {
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
                data = element.data('options') || element.data(), 
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
    function _construct(elem) {
        return elem.each(function () {
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
// BASE WIDGET
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

