/**
 * mtree.js
 * 
 * Multiple tree plugin fron jquery
 */
/*jslint browser: true, onevar: true, undef: true, bitwise: true, strict: true */
/*global jQuery */
"use strict";
(function ($) {
	"use strict";
	$.mtree = (function() {
		
		function console_logger(msg) {
			if (typeof console !== "undefined" && typeof console.debug !== "undefined") {
				console.log(msg);
			}
		}
		
		// Private stuff
		var instances = [],
			plugins = {},
			extensions = {},
			_focused_instance = -1,
			_iconhtml = "<ins class='ui-icon'>&#160;</ins>",
			_logger = {
				log: function(msg,level) {console_logger(msg);},
				debug : function(msg) {console_logger(msg);},
				error : function(msg) {console_logger(msg);}				
			},
			defaults = {
				logger: _logger,
				show: true,
				strings: {
				    new_node: 'new node'
				},
				getparams: $.param,
				requestParams: {},
				requestMethod: 'get',
				loadingClass: 'loading',
				views: ['tree','crumbs'],
				plugins: [],
				default_type: {
				    max_children  : -1,
                    max_depth     : -1,
                    open_icon: 'ui-icon-folder-open',
                    closed_icon: 'ui-icon-folder-collapsed'
				},
				theme : {
					dots : true,
					icons : true
					}
			};
		
		function get_focused_instance() {
			return instances[_focused_instance] || null;
		}
		
		/**
		 * Create an object which stores mtree data
		 * and the container associated with it
		 */
		function make_instance(index_, container_, settings_) {
			return {
				data: {},
				logger: function() { return settings_.logger; },
				settings: function() { return settings_; },
				index: function() { return index_; },
				container: function() { return container_; }
			};
		}
		
		// Return the Object
		return {
			num_plugins: function() {
				var size = 0, key;
				for(key in plugins) {
					if(plugins.hasOwnProperty(key)) size++;
				}
				return size;
			},
			//
			count: function() {return instances.length;},
			//
			defaults: function() {return $.extend(true, {}, defaults);},
			// Return a mtree instance from an elem
			instance: function(elem) {
				// get by instance id
				if(instances[elem]) { return instances[elem]; }
				// get by DOM (if still no luck - return null
				var o = $(elem); 
				if(!o.length && typeof elem === "string") { o = $("#" + elem); }
				if(!o.length) { return null; }
				return instances[o.closest(".mtree").data("mtree-instance-id")] || null;
			},
			focused_instance: function() {
				return get_focused_instance();
			},
			set_focused_instance: function(instance) {
				if(_focused_instance !== instance.index()) {
					var f = get_focused_instance();
					if(f) {
						f.container().removeClass("mtree-focused"); 
					}
					instance.container().addClass("mtree-focused"); 
					_focused_instance = instance.index();
				}
			},
			//
			// Add new plugin to the plugin object
			plugin: function(pname, pdata) {
				pdata = $.extend({}, {
					init_instance : $.noop, 
					del_instance : $.noop,
					defaults : false
				}, pdata);
				plugins[pname] = pdata;
				var pextensions = {};
				
				// Add plugin defaults to global defaults
				defaults[pname] = pdata.defaults;
				//
				if(pdata.is_default) {
					defaults.plugins.push(pname);
				}
				//
				// Set up extension calls for instance
				$.each(pdata.extensions, function(name, extension) {
				    var ename = name,
				        callable_extension;
				    
				    if(name.indexOf("_") === 0) {
                        ename = name.substring(1);
                    }
					//
					// Simple function is prefixed by '_'
				    callable_extension = function () {
				        var rslt,
				            _plgins = this.settings().plugins,
                            func = extension,
                            args = Array.prototype.slice.call(arguments),
                            rlbk = false,
                            super_method, evnt, self,
                            this_ = this;
				        
				        // Check if function belongs to the included plugins of this instance
	                    do {
	                        if($.inArray(func.plugin, _plgins) !== -1) { break; }
	                        func = func.__super;
	                    } while(func);
	                    if(!func) { return; }
	                    
	                    super_method = func.__super;
	                    if(name === ename) {
							evnt = new $.Event("mtree.before");
							self = this.container();
		
							// a chance to stop execution (or change arguments): 
							// * just bind to mtree.before
							// * check the additional data object (func property)
							// * call event.stopImmediatePropagation()
							// * return false (or an array of arguments)
							rslt = self.triggerHandler(evnt,
							        {"func" : name,
							         "inst" : this,
							         "args" : args });
							if(rslt === false) { return; }
							if(typeof rslt !== "undefined") { args = rslt; }
							
							this_ = $.extend({}, this, { 
									__callback : function (data) { 
										self.triggerHandler( name + '.mtree',
												{ "inst" : this,
										          "args" : args,
										          "rslt" : data,
										          "rlbk" : rlbk,
										          "name" : name});
									},
									__rollback : function () { 
									    rlbk = this.get_rollback();
									    return rlbk;
									},
									__super: function() {
									    return super_method.apply(this, args);
									}
								});
	                    }
						else if(super_method) {
						    this_ = $.extend({},this,{
                                    __super: function() {
                                        return super_method.apply(this, args);
                                    }
                            });
                        }
	                    return func.apply(this_, args);
					};
	                
	                extension.plugin = pname;
	                callable_extension.plugin = pname;
	                //extension.name = ename;
	                //callable_extension.name = ename;
	                extension.__super = extensions[ename];
	                pextensions[ename] = extension;
	                extensions[ename] = callable_extension
				});
				pdata.extensions = pextensions;
			},
			//
			// Rollback instances
            rollback : function (rb) {
                if(rb) {
                    if(!$.isArray(rb)) { rb = [ rb ]; }
                    $.each(rb, function (i, val) {
                        instances[val.index].set_rollback(val.html, val.data);
                    });
                }
            },
			/**
			 * Create jQuery plugins
			 */
			make_jquery: function (settings) {
			    settings = settings || {};
                settings.plugins = $.isArray(settings.plugins) ? settings.plugins : defaults.plugins;
                
				return this.each(function() {
					var instance_id = $.data(this, "mtree-instance-id"),
						opts, instance;
					if(typeof instance_id !== "undefined" && instances[instance_id]) {
						instances[instance_id].destroy();
					}
					instance_id = parseInt(instances.push({}),10) - 1;
					$.data(this, "mtree-instance-id", instance_id);
					opts = $.extend(true, {}, defaults, settings);
					opts.plugins = settings.plugins;
					
					instance = instances[instance_id] =
							make_instance(
									instance_id,
									$(this).addClass('mtree mtree'+instance_id)
									       .addClass('ui-widget'),
									opts);
					opts = instance.settings();
					
					$.each(extensions, function(name,extension) {
					    instance[name] = extension; //$.proxy(extension,instance);
					});
					// Loop over plugins in the instance settings and add extensions
					$.each(opts.plugins, function (idx, pname) {
						var plugin = plugins[pname];
						if(plugin) {
							opts.logger.debug('Installing extensions from ' + pname);
							instance.data[pname] = {};
							plugin.init_instance.apply(instance);
						}
					});
					// initialize the instance
					instance.init();
				});
			},
			//
			//Some usefule constants
			iconhtml: function() { return _iconhtml; }
		};
	})();
	
	$.fn.extend({
        mtree: $.mtree.make_jquery
	});
	
	/**
	 * The core plugin defines all the basic functionalities
	 */
	$.mtree.plugin("core", {
		// if this is set to true, the plugin will appear in the $.mtree.defaults()
		is_default: true,
		// called when initializing a tree instance
		init_instance : function () {
			var opts = this.settings(),
				self = this.container();
			this.data.core.to_open = $.map(
					$.makeArray(opts.core.initially_open), function (n) {
				return "#" + n.toString().replace(/^#/,"").replace('\\/','/').replace('/','\\/');
			});
		},
		// defaults parameters to be added to settings[plugin_name]
		defaults : {
			html_titles	: false,
			animation	: 200,
			initially_open : [],
			rtl			: false,
			strings		: {
				loading		: "Loading ...",
				new_node	: "New node"
			},
			indent: 18
		},
		extensions : {
			init: function () {
				this.set_focus();
				this.initial_layout();
				var self = this.container(),
					root = this.root(),
					opts = this.settings(),
					logger = this.logger();
				
				this.data.core.li_height = root.find("ul li.mtree-closed, ul li.mtree-leaf").eq(0).height() || 18;
				
				self.delegate("li > ins", "click.mtree", $.proxy(function (event) {
						var trgt = $(event.target);
						if(trgt.is("ins") && event.pageY - trgt.offset().top < this.data.core.li_height) {
							this.toggle_node(trgt);
						}
					}, this))
					.bind("mousedown.mtree", $.proxy(function () { 
						if(!this.is_focused()) {
							this.set_focus();
						}
					}, this))
					.bind("dblclick.mtree", function (event) {
					    logger.debug('Doubleclick event');
    					var sel;
    					if(document.selection && document.selection.empty) {
    					    document.selection.empty();
    					}
    					else {
    						if(window.getSelection) {
    							sel = window.getSelection();
    							try { 
    								sel.removeAllRanges();
    								sel.collapse();
    							} catch (err) { }
    						}
    					}
				    });
				this.__callback();
				this.load_node(-1, function () { this.loaded(); this.reopen(); });
			},
			_initial_layout: function() {
			    $('<ul>').appendTo(this.container());
			},
			_root: function() {
				return this.container();
			},
			destroy: function () { 
				
			},
			set_focus: function () {
				$.mtree.set_focused_instance(this);
				this.__callback();
			},
			//
			_is_open	: function (obj) { obj = this.node(obj); return obj && obj !== -1 && obj.hasClass("mtree-open"); },
			_is_closed	: function (obj) { obj = this.node(obj); return obj && obj !== -1 && obj.hasClass("mtree-closed"); },
			_is_leaf	: function (obj) { obj = this.node(obj); return obj && obj !== -1 && obj.hasClass("mtree-leaf"); },
			//
			// Type of node
	        _get_type : function(obj) {
                return this.settings().default_type;
            },
            // Set the node as closed. Behaviour controll by the node type
            // Check get_type
            _set_closed: function(obj) {
                var t = this.get_type(obj);
                obj.removeClass("mtree-open").addClass("mtree-closed");
                obj.children('ins').removeClass('ui-icon-minus').addClass('ui-icon-plus');
                $('ins',obj.children('a')).removeClass(t.open_icon).addClass(t.closed_icon);
            },
            _set_opened: function(obj) {
                var t = this.get_type(obj);
                obj.removeClass("mtree-closed").addClass("mtree-open");
                obj.children('ins').removeClass('ui-icon-plus').addClass('ui-icon-minus');
                $('ins',obj.children('a')).removeClass(t.closed_icon).addClass(t.open_icon);
            },
            // set the roolback
            set_rollback : function (html, data) {
                this.root().html(html);
                this.data = data;
                this.__callback();
            },
            // rollback
            get_rollback : function () { 
                this.__callback();
                return {
                        index: this.index(),
                        html: this.root().children("ul").clone(true),
                        data: this.data
                        }; 
            },
			//
			// open/close
			open_node	: function (obj, callback, skip_animation) {
				obj = this.node(obj);
				if(!obj.length) { return false; }
				if(!obj.hasClass("mtree-closed")) { if(callback) { callback.call(); } return false; }
				var s = skip_animation ? 0 : this.settings().core.animation,
					t = this;
				if(!this.is_loaded(obj)) {
					obj.children("a").addClass("mtree-loading");
					this.load_node(obj, function () { t.open_node(obj, callback, skip_animation); }, callback);
				}
				else {
					if(s) { obj.children("ul").css("display","none"); }
					this.set_opened(obj);
					obj.children("a").removeClass("mtree-loading");
					if(s) { obj.children("ul").stop(true).slideDown(s, function () { this.style.display = ""; }); }
					this.__callback({ "obj" : obj });
					if(callback) { callback.call(); }
				}
			},
			//
			// close
			close_node	: function (obj, skip_animation) {
				obj = this.node(obj);
				var s = skip_animation ? 0 : this.settings().core.animation;
				if(!obj.length || !obj.hasClass("mtree-open")) { return false; }
				if(s) { obj.children("ul").attr("style","display:block !important"); }
				this.set_closed(obj);
				if(s) { obj.children("ul").stop(true).slideUp(s, function () { this.style.display = ""; }); }
				this.__callback({ "obj" : obj });
			},
			//
			// True if node is on focus
			_is_focused: function () {
				var f = $.mtree.focused_instance();
				return f && f.index() === this.index(); 
			},
			_selector: function() {return 'li';},
			//
			// Get the node
			_node: function(obj) {
				if(obj === -1) { return -1; }
				var root = this.root(),
				$obj = $(obj, root); 
				$obj = $obj.closest("li", root);
				return $obj.length ? $obj : false;
			},
			//
			_get_text : function (obj) {
                obj = this.node(obj);
                if(!obj.length) { return false; }
                var s = this.settings().core.html_titles;
                obj = obj.children("a:eq(0)");
                if(s) {
                    obj = obj.clone();
                    obj.children("INS").remove();
                    return obj.html();
                }
                else {
                    obj = obj.contents().filter(function() { return this.nodeType == 3; })[0];
                    return obj.nodeValue;
                }
            },
            //
            set_text    : function (obj, val) {
                obj = this.node(obj);
                if(!obj.length) { return false; }
                obj = obj.children("a:eq(0)");
                if(this.settings().core.html_titles) {
                    var tmp = obj.children("INS").clone();
                    obj.html(val).prepend(tmp);
                    this.__callback({ "obj" : obj, "name" : val });
                    return true;
                }
                else {
                    obj = obj.contents().filter(function() { return this.nodeType == 3; })[0];
                    this.__callback({ "obj" : obj, "name" : val });
                    return (obj.nodeValue = val);
                }
            },
			//
			// Trivial algorithm for generation a unique ID for nodes
			_unique_id: function() {
				var self = this.container(),
					index = this.index(),
					ok = false,
					uniqueNum, uid;
				for(;;) {
					uid = 'mt-'+index+'-'+Math.floor( Math.random()*999999 );
					if(!$('#'+uid,self).length) {break;}
				}
				return uid;
			},
			//
			// UTILITY: create the inner html of a node
			_make_inner: function(obj,data) {
			    var s = this.settings(),
			        data = data || {},
			        name = data.name || s.strings.new_node,
			        href = data.href || '#';
			    obj.append("<ins class='ui-icon'>&#160;</ins>");
			    return $("<a>"+name+"</a>")
			             .attr('href',href)
                         .prepend("<ins class='ui-icon'>&#160;</ins>");
			},
			//
			// Get the parent
			_parent: function (obj) {
				obj = this.node(obj);
				if(obj === -1 || !obj) { return false; }
				var o = obj.parentsUntil(".mtree", "li:eq(0)");
				return o.length ? o : -1;
			},
			//
			// get children
			_children: function (obj) {
				obj = this.node(obj);
				if(!obj) { return false; }
				if(obj === -1) { obj = this.container(); }
				return obj.children("ul:eq(0)").children("li");
			},
			// Toggle
			_toggle_node: function(obj) {
				obj = this.node(obj);
				if(obj.hasClass("mtree-closed")) { return this.open_node(obj); }
				if(obj.hasClass("mtree-open")) { return this.close_node(obj); }
			},
			//
			// Insert Node utility
			_insert_node: function(d, obj, position, callback) {
			    var pobj, tmp, ul;
			    
			    this.set_closed(d);
			    
			    if(position == "before") {
                    obj.before(d);
                    pobj = this.parent(obj);
                }
                else if (position == "after") {
                    obj.after(d);
                    pobj = this.parent(obj);
                }
                else {
                    if(obj === -1) {
                        obj = this.root();
                        if(position === "before") { position = "first"; }
                        if(position === "after") { position = "last"; }
                    }
                    ul = obj.children("ul");
                    if(!ul.length) {
                        ul = $('<ul>').appendTo(obj);
                    }
                    pobj = obj;
                    switch(position) {
                        case "inside":
                        case "first" :
                            ul.prepend(d);
                            break;
                        case "last":
                            ul.append(d);
                            break;
                        default:
                            if(!position) { position = 0; }
                            tmp = ul.children("li").eq(position);
                            if(tmp.length) { tmp.before(d); }
                            else { ul.append(d); }
                            break;
                    }
                }
                this.clean_node(pobj);
                callback.call(this,{ "obj" : d, "parent" : pobj });
			},
			//
			clean_node	: function (obj) {
				obj = obj && obj !== -1 ? $(obj) : this.container();
				obj = obj.is("li") ? obj.find("li").andSelf() : obj.find("li");
				obj.removeClass("mtree-last")
					.filter("li:last-child").addClass("mtree-last").end()
					.filter(":has(li)")
						.not(".mtree-open").removeClass("mtree-leaf").addClass("mtree-closed");
				obj.not(".mtree-open, .mtree-closed").addClass("mtree-leaf").children("ul").remove();
				this.__callback({ "obj" : obj });
			},
			//
			/** Create a new node in a defined position with respect an object obj
			 * @param obj a portfolio Object or -1
			 * @param data data to add
			 * @return a jQuery object containing the node
			 */
			create_node	: function (obj, data, position, callback, is_loaded) {
				obj = this.node(obj);
				if(!obj) { return false; }
				
				var d = $("<li>"),
					s = this.settings().core,
					iconhtml = $.mtree.iconhtml(),
					ul,	tmp;

				if(!is_loaded && !this.is_loaded(obj)) {
					this.load_node(obj, function () {
						this.create_node(obj, position, js, callback, true);
					});
					return false;
				}

				//this.__rollback();
				this.make_inner(d,data).appendTo(d);
				this.insert_node(d, obj, position, this.__callback);
				if(callback) { callback.call(this, d); }
				return d;
			},
			//
			// Basic operations: deleting nodes
            delete_node : function (obj) {
                obj = this.node(obj);
                if(!obj.length) { return false; }
                var p = this.parent(obj);
                obj = obj.remove();
                if(p !== -1) {
                    if(p.find("> ul > li").length === 0) {
                        p.removeClass("mtree-open mtree-closed").addClass("jstree-leaf");
                    }
                    this.clean_node(p);
                }
                return obj;
            },
			//
			// Dummy functions to be overwritten by any datastore plugin included
			load_node: function (obj) {
				this.__callback({ "obj" : obj });
			},
			_is_loaded	: function (obj) { return true; }
		}
	});
	
	/**
	 * JSON data plugin
	 * 
	 * Load data from server or parse user defined data.
	 */
	$.mtree.plugin("json", {
		is_default: true,
		defaults : {
			url	: null,
			data: null
		},
		extensions : {
			load_node: function(obj, callback, errback) {
				var that = this;
				this.load_node_json(
						obj,
						function () {
							that.__callback({ "obj" : obj });
							callback.call(this);
							},
						errback);
			},
			//
			// Load a new node into the tree
			load_node_json: function(obj, callback, errback) {
				var s = this.settings().json,
					self = this.container();
				obj = this.node(obj);
				//
				// Bail out early if tree is loading
				if(obj && obj !== -1) {
					if(obj.data("mtree-is-loading")) {
						return;
					} else {
						obj.data("mtree-is-loading",true);
					}
				}
				
				// Tree not yet available. Build it.
				if(!obj || obj === -1) {
					// AJAX loading
					if(s.url) {
					    if($.isFunction(s.url)) {
					        s.url.call(this);
					    }
					    else {
						  throw "Ajax loading not implemented yet Not implemented";
					    }
					}
					// data is given
					else if(s.data) {
						this.parse_json(obj, s.data);
					}
					else {
						throw "Neither data nor url ajax settings supplied.";
					}
				}
			},
			//
			// This function expect a node or a list of nodes
			_parse_json: function(obj, js) {
				var that = this;
				if(!js) { return false; }
				if($.isFunction(js)) { 
					js = js.call(this);
				}
				if(obj === -1) {
					this.root().empty();
				}
				// this is a node
				if('name' in js) {
					obj = this.create_node(obj, js);
					js = js.children;
				}
				else if('children' in js) {
					js = js.children;
				}
				if($.isArray(js)) {
					$.each(js, function(idx,node) {
						that.parse_json(obj, node);
					});
				}
			}
		}
	});
	
}(jQuery));