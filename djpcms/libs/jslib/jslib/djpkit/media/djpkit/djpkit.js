/**
 * djpkit as swiss knife singletone object
 * for user interfaces.
 * 
 * Version: @VERSION
 * Date: @DATE
 */
/*jslint browser: true, onevar: true, undef: true, bitwise: true, strict: true */
/*global jQuery */
(function($) {
    
    $.djpkit = (function() {
        var that,
            plugins = {},
            panels = [],
            cn = 'djpkit-floating',
            current = [],
            show_event = 'djpkit.show',
            hide_event = 'djpkit.hide';
        
        function show() {
            var elem = current[0];
            if(elem) {
                elem.obj._show.apply(elem.obj, elem.args);
                $(document).triggerHandler(show_event);
            }
        }
        
        // Create a floating panel
        function make_panel(name, self) {
            var cnt = self.container().addClass(cn);
            $('body').append(cnt.hide());
            self.register_events();
            
            self = $.extend(self, {
                show: function() {
                    current.unshift(
                            {
                                obj: self,
                                args: arguments
                            });
                    if(current.length == 1) {show();}
                }
            });
            panels.push(self);
            return self;
        }
        
        function tryClose() {
            var c = current.pop(),
                obj;
            if(c) {
                obj = c.obj;
                if($.isFunction(obj.handle_blur)) {
                    obj.handle_blur();
                }
                else {
                    obj.container().hide();
                    $(document).triggerHandler(hide_event,c.obj.name);
                }
                show();
            }            
        }
        
        that = {
            version: "@VERSION",
            plugin: function(pname, plugin_data) {
                plugin_data.name = pname;
                plugins[pname] = plugin_data;
            }
        };
        
        $(document).ready(function() {
            $.each(plugins, function(name,plg) {
                that[name] = make_panel(name,plg);
            });
            // Register the click event to hide panels
            $('body').click(function(event) {
                tryClose();
            });
        });
        
        return that;
    }());
    
    
    /**
     * Context menu plugin.
     * A singletone panel for displaying a right-click menu on a page.
     */
    $.djpkit.plugin("context", (function() {
        // Private data
        var _cn = 'ui-widget ui-widget-content',
            cnt = $("<div id='contextmenu'>").addClass(_cn).css({'z-index':9999}),
            target = null,
            vis = false,
            that, par, data, func;
        
        function exec(i) {
            if($.isFunction(func[i])) {
                func[i].call(data, par);
                return true;
            }
            else { return false; }
        }
        
        // Parse the entry object
        function parse(s, is_callback) {
            if(!s) { return false; }
            var str = "",
                tmp = false;
            if(!is_callback) { func = {}; }
            str += "<ul>";
            $.each(s, function (i, val) {
                if(!val) { return true; }
                if(!val.name) {
                    str += "<li class='separator'></li>";
                }
                else {
                    func[val.name] = val.action;
                    str += "<li class='ui-state-default'><a href='#' rel='" + val.name + "'><ins";
                    if(val.icon) {
                        if(val.icon.indexOf("/") === -1) {
                            str += " class='" + val.icon + "' ";
                        }
                        else {
                            str += " style='background:url(" + val.icon + ") center center no-repeat;' ";
                        }
                    }
                    str += ">&#160;</ins>";
                    if(val.submenu) {
                        str += "<span style='float:right;'>&raquo;</span>";
                    }
                    str += val.label + "</a>";
                    if(val.submenu) {
                        tmp = parse(val.submenu, true);
                        if(tmp) { str += tmp; }
                    }
                    str += "</li>";
                }  
            });
            str += "</ul>";
            return str.length > 10 ? str : false;
        }
            
        that = {
                container: function() {
                    return cnt;
                },
                register_events: function() {
                    cnt.delegate('li','mouseenter',function() {
                        $(this).addClass('ui-state-hover');
                    }).delegate('li','mouseleave',function() {
            		    $(this).removeClass('ui-state-hover');
            		}).delegate('li','click',function() {
                        var fname = $('a',this).attr('rel');
                        exec(fname);
            		});
        	    },
            	// Show the context menu
                _show : function(s, t, x, y, d, p) {
                    var html = parse(s), h, w, dw, dh;
                    if(!html) { return; }
                    vis = true;
                    target = t;
                    par = p || t || null;
                    data = d || null;
                    cnt.html(html).css({"visibility" : "hidden",
                                        "display" : "block",
                                        "left" : 0, "top" : 0 });
                    dw = $(document).width();
                    dh = $(document).height();
                    h = cnt.height();
                    w = cnt.width();
                    if(x + w > dw) { 
                        x = dw - (w + 5); 
                        cnt.find("li > ul").addClass("right"); 
                    }
                    if(y + h > dh) { 
                        y = y - (h + t[0].offsetHeight); 
                        cnt.find("li > ul").addClass("bottom"); 
                    }
                    
                    cnt.css({"visibility" : "visible",
                             "left" : x, "top" : y });
                },
                exec: function(i) {
                    if($.isFunction(that.func[i])) {
                        that.func[i].call(that.data, that.par);
                        return true;
                    }
                    else { return false; }
                }
        };
        return that;
    }()));
    
    
    $.djpkit.plugin("input", (function() {
        // A floating input singletone
        var cnt = $('<input id="floating-input">'),
            default_margin = 4,
            callback, that;
        
        that = {
                container: function() {
                    return cnt;
                },
                register_events: function() {
                },
                handle_blur: function() {
                    if($.isFunction(callback)) {
                        callback(cnt.val());
                    }
                },
                _show: function(el, data) {
                    var h = el.height() + "px",
                        margin = data.margin ? data.margin : default_margin,
                        rtl = data.rtl,
                        val = data.val || "";
                        w = Math.max(el.width() - margin,70) + 'px';
                    callback = data.callback;
                    cnt.val(val).appendTo(el)
                       .css({"margin-left"  : (rtl ? "auto" : margin + "px"),
                             "margin-right" : (rtl ? margin + "px" : "auto"),
                             "height" : h,
                             "lineHeight" : h,
                             "width" : w,
                             "display": 'inline'
                        }).focus().show();
                }
            };
        return that;
    }()));
    
}(jQuery));
