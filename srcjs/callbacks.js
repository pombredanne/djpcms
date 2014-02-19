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
        return el;
    }
});
