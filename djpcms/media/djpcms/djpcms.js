/* Description:  djpcms Javascript Site Manager
 * Author:       Luca Sbardella
 * Language:     Javascript
 * License:      new BSD licence
 * Contact:      luca.sbardella@gmail.com
 * web:			 https://github.com/lsbardel/djpcms
 * @requires:	 jQuery, jQuery-UI
 * 
 * Copyright (c) 2009-2011, Luca Sbardella
 * New BSD License 
 * http://www.opensource.org/licenses/bsd-license.php
 *
 */
/**
 * 
 * djpcms site handle
 * 
 * @param _media_url_base,	String base url for media files
 * @param options_, Object page-specific options
 */
(function($) {
    
    /**
     * Common Ancestor jQuery plugin
     */
    $.fn.commonAncestor = function() {
        if(!this.length) {
            return $([]);
        }
        var parents = [],
            minlen = Infinity,
            i,j,p,equal;
    
        this.each(function() {
            var curparents = $(this).parents();
            parents.push(curparents);
            minlen = Math.min(minlen, curparents.length);
        });
    
        $.each(parents, function(i,p) {
            parents[i] = p.slice(p.length - minlen);
        });
    
        // Iterate until equality is found
        for(i=0;i<parents[0].length;i++) {
            p = parents[0][i];
            equal = true;
            for(j=1;j<parents.length;j++) {
                if(parents[j][i] !== p) {
                    equal = false;
                    break;
                }
            }
            if(equal) {
                return $(p);
            }
        }
        return $([]);
    };
    
    /**
     * A minimalist logging class
     */
    function djplogger() {
        function error(msg, e){
            if(e) {
                msg += "- File " + e.fileName + " - Line " + e.lineNumber + ": " + e;
            }
            return msg;
        }
        
        var handlers = [],
            logclass = 'log',
            level = 10,
            levels = {
                    debug: {n:10,v:'DEBUG'},
                    info: {n:20,v:'INFO'},
                    warn: {n:30,v:'WARN'},
                    error: {n:40,v:'ERROR',f: error},
                    critical: {n:50,v:'CRITICAL', f:error}
                },
            mapping = {};
            names = {};
        $.each(levels,function(fname,val) {
            mapping[val.n] = val.v;
            names[val.v] = val.n;
        });
        
        var instance = {
            'level': function() {return level;},
            'set_level': function(lev) {
                var l = names[lev];
                if(l) {
                    level = l;
                }
            },
            'addHandler': function(h) {handlers.push(h);}
        };
            
        if(typeof console !== "undefined" && typeof console.log !== "undefined") {
            instance.addHandler(function(msg,level) {
                console.log(msg);
            });
        }
            
        instance.log = function (msg, lvl) {
            if(lvl < level) {return;}
            var mlevel = mapping[lvl] || 'UNKN',
                msg,
                dte = new Date(),
                hours = dte.getHours(),
                minutes = dte.getMinutes(),
                seconds = dte.getSeconds();
            if(hours < 10) {hours = '0'+hours;}
            if(minutes < 10) {minutes = '0'+minutes;}
            if(seconds < 10) {seconds = '0'+seconds;}
            msg = hours+':'+minutes+':'+seconds+' - '+mlevel+' - '+msg;
            msg = '<pre class="' + logclass + ' '+mlevel.toLowerCase()+'">'+msg+'</pre>';
            $.each(handlers, function(i,handle) {
                handle(msg,level);
            });
        }
        
        $.each(levels,function(fname,val) {
            instance[fname] = function (msg,e) {
                if(val.f) {
                    msg = val.f(msg,e);
                }
                instance.log(msg,val.n);
            }
        });
        
        return instance;
    };
    
    /**
     * djpcms site manager
     */
    $.djpcms = (function() {
        
        var decorators = {},
            actions = {},
            jsonCallBacks = {},
            logging_pannel = null,
            inrequest = false,
            panel = null,
            appqueue = [],
            logger = djplogger(),
            defaults = {
    	        media_url: "/media/",
    	        confirm_actions:{
    	            'delete': 'Please confirm delete',
    	            'flush': 'Please confirm flush'
    	                },
    	        autoload_class: "autoload",
    	        ajax_server_error: "ajax-server-error",
    	        errorlist: "errorlist",
    	        formmessages: "form-messages",
    	        box_effect: {type:"blind",duration:500},
    	        remove_effect: {type:"drop",duration:500},
    	        bitly_key: null,
    	        twitter_user: null,
    	        fadetime: 200,
    	        ajaxtimeout: 30,
    	        debug: false
    	        };
    	
    	function set_logging_pannel(panel) {
    	    var panel = $(panel);
    	    if(panel.length) {
    	        logger.addHandler(function(msg,level) {
    	            panel.prepend(msg);
    	        });
    	    }
    	}
    	    	
    	function ajaxparams(name, data) {
    	    var p = {'xhr':name};
    	    if(data) {
    	        return $.extend(p,data);
    	    }
    	    else {
    	        return p;
    	    }
    	}
    	
    	function queue_application(app) {
    	    if($.data(document,'djpcms')) {
    	        app();
    	    }
    	    else {
    	        appqueue.push(app);
    	    }
    	}
    	
    	// Set options
    	function setOptions(options_) {
    		$.extend(true, defaults, options_);
    	}
    	
    	// Add a new decorator
    	function addDecorator(deco) {
    	    var config = deco.config || {},
    	        opts = defaults[deco.id] || {}; 
    		decorators[deco.id] = $.proxy(deco.decorate, deco);
    		defaults[deco.id] = $.extend(config,opts);
    	}
    	
    	// Add a new callback for JSON data
    	function addJsonCallBack(jcb) {
    		jsonCallBacks[jcb.id] = jcb;
    	}
    	
    	// Remove a decorator
    	function removeDecorator(rid) {
    		if(decorators.hasOwnMethod(rid)) {
    		    delete decorators[rid];
    		}
    	}
    	
    	function _jsonParse(data, elem) {
    	    var id  = data.header;
    	    var jcb = jsonCallBacks[id];
    	    if(jcb) {
    	        return jcb.handle(data.body, elem, defaults) & data.error;
    	    }
    	    else {
    	        logger.error('Could not find callback ' + id);
    	    }
    	}
    	
    	function addAction(id, action) {
    	    var a = actions[id];
    	    if(!a) {
    	       a = {'action':action, 'ids': {}};
    	       actions[id] = a;
    	    } else if(action) {
    	        a.action = action;
    	    }
    	    return a;
    	}
    	
    	function registerActionElement(actionid, id) {
    	    var action = addAction(actionid,null);
    	    action.ids[id] = id;
    	}
    	
    	function getAction(actionid, id) {
    	    var action = addAction(actionid,null);
    	    if(action.ids[id]) {
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
    		if(status === "success") {
    			v = _jsonParse(data,elem);
    		}
    		inrequest = false;
    		return v;
    	}
    	
    	/**
    	 * DJPCMS Handler constructor
    	 */
    	function _construct() {
    		return this.each(function() {
    			var config = defaults;
    			var me = $(this);
    			var lp = $('.djp-logging-panel',me);
    			if(lp) {
    				set_logging_pannel(lp);
    			}
    			
    			$.each(decorators,function(id,decorator) {
    				logger.info('Adding decorator ' + id);
    				decorator(me,config);
    			});
    			if(this == document) {
    			    $.data(this,'djpcms',config);
    			    $.each(appqueue, function(i,app) {
    			        app();
    			    });
    			    appqueue = [];
    			}
    		});
    	}
    	
    	//    API
    	return {
    	    construct: _construct,
    	    options: defaults,
    	    jsonParse: _jsonParse,
    	    'addJsonCallBack': addJsonCallBack,
    	    'jsonCallBack': _jsonCallBack,
    	    decorator: addDecorator,
    	    set_options: setOptions,
    	    'ajaxparams': ajaxparams,
    	    set_inrequest: function(v){inrequest=v;},
    	    //
    	    // Action in slements ids
    	    'addAction': addAction,
    	    'registerActionElement': registerActionElement,
    	    'getAction': getAction,
    	    //
    	    'inrequest': function(){return inrequest;},
    	    'logger': logger,
    	    'queue': queue_application,
    	    'panel': function() {
    	        // A floating panel
    	        if(!panel) {
                    panel = $('<div>').hide().appendTo($('body'))
                                    .addClass('float-panel ui-widget ui-widget-content ui-corner-all')
                                    .css({position:'absolute',
                                         'text-align':'left',
                                          padding:'5px'});
                }
    	        return panel;
    	    },
    	    smartwidth: function(html) {
    	        return Math.max(15*Math.sqrt(html.length),200);
    	    }
    	};
    }());
    
    
    /**
     * _____________________________________________ PLUGINS CALLBAKS AND DECORATORS
     * 
     */
    // extend plugin scope
    $.fn.extend({
        djpcms: $.djpcms.construct
    });
    
    
    $.djpcms.confirmation_dialog = function(title, html, callback, opts) {
        var el = $('<div title="'+title+'"></div>').html(html+""),
            options = $.extend({},opts,{
               modal: true,
               draggable: false,
               resizable: false,
               buttons: {
                   Ok : function() {
                       $( this ).dialog( "close" );
                       callback(true);
                   },
                   Cancel: function() {
                       $(this).dialog( "close" );
                       callback(false);
                   }
                }
            });
        return el.dialog(options);
    };
    
    $.djpcms.warning_dialog = function(title, warn, callback) {
        var opts = {
                dialogClass: 'ui-state-error',
                autoOpen: false},
            el = $.djpcms.confirmation_dialog(title, warn, callback, opts);
        $('.ui-dialog-titlebar, .ui-dialog-buttonpane',el.dialog('widget'))
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
    $.djpcms.ajax_loader =  function djpcms_loader(url,action,method,data,conf) {
        var sendrequest = function(callback) {
            var that = this;
            if(conf && !callback) {
                var el = $('<div></div>').html(conf);
                el.dialog({modal: true,
                           draggable: false,
                           resizable: false,
                           buttons: {
                               Ok : function() {
                                   $( this ).dialog( "close" );
                                   sendrequest(true);
                               },
                               Cancel: function() {
                                   $(this).dialog( "close" );
                                   $.djpcms.set_inrequest(false);
                               }
                    }});
            } else {
                $.ajax({
                        'url':url,
                        'type': method || 'post',
                        'dataType': 'json',
                        'success': function callBack(e,s) {
                            $.djpcms.set_inrequest(false);
                            $.djpcms.jsonCallBack(e,s,that);
                         },
                        'data': $.djpcms.ajaxparams(action,data)
                    });
            }
        };
        return sendrequest 
    };
    
    $.djpcms.ajax_loader_from_tool = function(tool) {
        if(tool.ajax) {
            return $.djpcms.ajax_loader(tool.url,
                                        tool.action,
                                        tool.method,
                                        tool.data,
                                        tool.conf);
        }
    }
    
    /**
     * A modal error dialog
     */
    $.djpcms.errorDialog = function(html,title) {
        title = title || 'Something did not work';
        var el = $('<div title="'+title+'"></div>').html(html+""),
            width = $.djpcms.smartwidth(html);
        el.dialog({modal:true,
                   autoOpen:false,
                   dialogClass: 'ui-state-error',
                   'width': width});
        $('.ui-dialog-titlebar',el.dialog('widget')).addClass('ui-state-error');
        el.dialog("open");
     };
    
    /**
     * ERROR and SERVER ERROR callback
     */
    $.djpcms.addJsonCallBack({
    	id: "error",
    	handle: function(data, elem) {
    	    $.djpcms.errorDialog(data);
    	}
    });
    $.djpcms.addJsonCallBack({
    	id: "servererror",
    	handle: function(data, elem) {
    	    $.djpcms.errorDialog(data,"Unhandled Server Error");
    	}
    });
    
    /**
     * empty callback
     */
    $.djpcms.addJsonCallBack({
        id: "empty",
        handle: function(data, elem) {
            return true;
        }
    });
    
    /**
     * collection callback
     */
    $.djpcms.addJsonCallBack({
    	id: "collection",
    	handle: function(data, elem) {
    		$.each(data, function(i,component) {
    			$.djpcms.jsonParse(component,elem);
    		});
    		return true;
    	}
    });
    
    /**
     * html JSON callback
     */
    $.djpcms.addJsonCallBack({
    	id: "htmls",
    	handle: function(data, elem, config) {
    		$.each(data, function(i,b) {
    			var el = $(b.identifier,elem),
    			    fade = config.fadetime,
    			    html;
    			if(!el.length & b.alldocument) {
    				el = $(b.identifier);
    			}
    			if(el.length) {
    				if(b.type === 'hide') {
    					el.hide();
    				}
    				else if(b.type === 'show') {
    					el.show();
    				}
    				else if(b.type === 'value') {
    					el.val(b.html);
    				}
    				else if(b.type === 'append') {
    					var nel = $(b.html).appendTo(el);
    					nel.djpcms();
    				}
    				else {
    				    el.show();
    				    el.fadeOut(fade,'linear',function(){
    				        if(b.type === 'replacewith') {
    				            el.replaceWith(b.html);
    				        }
    				        else {
    				            if(b.type === 'addto') {
    				                html = el.html() + b.html;
    				            }
    				            else {
    				                html = b.html;
    				            }
    				            el.html(b.html);
    				        }
    				        el.djpcms();
    				        el.fadeIn(fade);
    				        //el.show();
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
    	handle: function(data, elem) {
    		var selected = [];
    		$.each(data, function(i,b) {
    			var el;
    			if(b.alldocument) {
    				el = $(b.selector);
    			}
    			else {
    				el = $(b.selector,elem);
    			}
    			if(el.length) {
    				b.elem = el;
    			}
    		});
    		$.each(data, function(i,b) {
    			if(b.elem) {
    				b.elem.attr(b.attr,b.value);
    			}
    		});
    	}
    });
    
    /**
     * Remove html elements
     */
    $.djpcms.addJsonCallBack({
    	id: "remove",
    	handle: function(data, elem) {
    		$.each(data, function(i,b) {
    			var el = $(b.identifier,elem);
    			if(!el.length & b.alldocument) {
    				el = $(b.identifier);
    			}
    			if(el.length) {
    			    var be = $.djpcms.options.remove_effect;
    			    el.fadeIn(be.duration, function() {el.remove();});
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
    	handle: function(data, elem) {
    		window.location = data;
    	}
    });
    
    /**
     * Popup
     */
    $.djpcms.addJsonCallBack({
    	id: "popup",
    	handle: function(data, elem) {
    		$.popupWindow({windowURL:data,centerBrowser:1});
    	}
    });
    
    /**
     * Dialog callback
     * 
     * Create a jQuery dialog from JSON data
     */
    $.djpcms.addJsonCallBack({
    	id: "dialog",
    	handle: function(data, elem) {
    		var el = $('<div></div>').html(data.html).djpcms();
    		var buttons = {};
    		$.each(data.buttons,function(n,b) {
    			buttons[b.name] = function() {
    				b.d = $(this);
    				
    				b.dialogcallBack = function(data) {
    					$.djpcms.jsonCallBack(data,'success',el);
    					if(b.close) {
    						b.d.dialog("close");
    					}
    				};
    				
    				if(b.url) {
    					var params = $('form',el).formToArray();
    					if(b.func) {
    						var extra = $.djpcms.ajaxparams(b.func);
    						$.each(extra, function(k,v) {
    							params.push({'name':k, 'value':v});
    						});
    					}
    					$.post(b.url,$.param(params),b.dialogcallBack,"json");
    				}
    				else {
    					b.d.dialog('close');
    				}
    			};
    		});
    		var options = data.options;
    		options.buttons = buttons;
    		el.dialog(options);
    		return true;
    	}
    });
    
    
    ////////////////////////////////////////////////////////////////////////////////////////////////
    //						DECORATORS
    ////////////////////////////////////////////////////////////////////////////////////////////////
    
    $.djpcms.decorator({
        id:'anchors',
        description:'Decorate anchors button and submits',
        config: {
            blank_target: true,
            jquery: true
        },
        decorate: function(obj, config) {
            var options = config.anchors,
                jquery = options.jquery,
                bt = options.blank_target;
           
            if(jquery) {
                $('input[type="submit"]',obj).each(function(){
                    var el = $(this);
                    if(!el.hasClass('nobutton')) {
                        el.button();
                    }
                });
                $('button',obj).each(function() {
                    var el = $(this),
                        data = el.data(),
                        icon = data.icon,
                        text = data.text;
                    if(!text) {
                         text = icon ? false : true;
                    }
                    el.button({
                        icons:{primary:icon},
                        text:text
                    });
                });
            }
            if(bt || jquery) {
                $('a',obj).each(function() {
                    var a = $(this), href;
                    if(jquery && a.hasClass('button')) {
                        var sp = a.children('span'),
                            opts,ico;
                        if(sp.length) {
                            ico = sp[0].className;
                            sp.remove();
                        }
                        if(ico) {
                            opts = {icons:{primary:ico}};
                            if(!a.html()) {opts.text = false;}
                        }
                        a.button(opts).removeClass('djph');
                    }
                    if(bt) {
                        var href = a.attr('href');
                        if(href && href.substring(0,4) == 'http') {
                            a.attr('target','_blank');
                        }
                    }
                });
            }
        }
    });
    
       /**
     * Accordion menu
     */
    /*
    $.djpcms.decorator({
        id:"accordion_menu",
        decorate: function($this,config) {
            $('ul.accordionmenu',$this).each(function() {
                var menu = $(this);
                var act = $('li.selected a',menu);
                if(!act.length) {
                    act = 0;
                }
                var el = menu.accordion({header: "a.menuitem",
                                         event: "mouseover",
                                         active: act});
                menu.fadeTo(config.fadetime,1);
            });
        }
    });*/
    
    $.djpcms.decorator({
        id:"accordion",
        config:{
            effect:'drop',
            fadetime: 500,
            accordion : {
                autoHeight:false,
                fillSpace:false
                }
            },
        decorate: function($this,config) {
            var c = config.accordion;
            $('.ui-accordion',$this).accordion(c.accordion)
                                    .show(c.effect,{},c.fadetime);
        }
    });
    
    /**
     * jQuery UI Tabs
     */
    $.djpcms.decorator({
        id:"ui_tabs",
        config:{
            effect:'drop',
            fadetime: 500,
           //tabs: {cookie: {expiry: 7}},
            },
        decorate: function($this, config) {
            var c = config.ui_tabs;
            $('.ui-tabs',$this).tabs(config.tabs).show(c.effect,{},c.fadetime);
        }
    });

    $.djpcms.decorator({
        id:'ui-state-hover',
    	decorate: function(obj, config) {
    	    $('.edit-menu a',obj).addClass('ui-corner-all')
    	        .mouseenter(function(){$(this).addClass('ui-state-hover');})
    	        .mouseleave(function(){$(this).removeClass('ui-state-hover');});
    	    $('a.ui-hoverable',obj).addClass('ui-corner-all')
                .mouseenter(function(){$(this).addClass('ui-state-hover');})
                .mouseleave(function(){$(this).removeClass('ui-state-hover');});
    	}
    });
    
    
    /**
     * Ajax links, buttons and select 
     */
    $.djpcms.decorator({
        id:	"ajax_widgets",
        config: {
            selector_link: 'a.ajax, button',
            selector_select: 'select.ajax',
            selector_form: 'form.ajax',
            submit_opacity: '0.5'
        },
        description: "add ajax functionality to links, buttons and selects",
        decorate: function($this,config) {
            var confirm = config.confirm_actions,
                cfg = config.ajax_widgets,
                callback = $.djpcms.jsonCallBack,
                logger = $.djpcms.logger,
                that = this;
            
            function presubmit_form(formData, jqForm, opts) {
                jqForm.css({'opacity':cfg.submit_opacity});
                //$('.'+config.errorlist+
                // ',.'+config.ajax_server_error,jqForm).fadeOut(100);
                return true;
            }
            
    		$(cfg.selector_link,$this).click(function(event) {
    		    event.preventDefault();
    		    var elem = $(this),
    		        ajax = elem.hasClass('ajax'),
    		        conf = elem.data('warning');
    		    
    		    function handleClick(handle) {
    		        var url = elem.attr('href') || elem.data('href') || '.';
    		        if(!handle) {return;}
    		        if(!elem.hasClass('ajax')) {
    		            window.location = url;
    		        } else {
                        var method = elem.data('method') || 'post',
                            action = elem.attr('name');
                        $.djpcms.ajax_loader(url,action,method,{})();
    		        }
    		    }
    		    
    		    if(conf) {
    		        var title = conf.title || '',
    		            body = conf.body || conf;
    		        $.djpcms.warning_dialog(title,body,handleClick);
    		    }
    		    else {
    		        handleClick(true);
    		    }
    		});
    		
    		$(cfg.selector_select,$this).change(function(event) {
    			var elem = $(this),
    			    url = elem.attr('href'),
    			    f = elem.parents('form');
    			if(f.length === 1 && !url) {
    				url = f.attr('action');
    			}
    			if(!url) {
    				url = window.location.toString();
    			}
    			
    			if(!f) {
    				var p   = $.djpcms.ajaxparams(elem.attr('name'));
    				p.value = elem.val();
    				$.post(_url,$.param(p),$.djpcms.jsonCallBack,"json");
    			}
    			else {
    				var opts = {
    						'url':     url,
    						type:      'get',
    						success:   callback,
    						submitkey: config.post_view_key,
    						dataType: "json"
    						};
    				f[0].clk = elem[0];
    				logger.info('Submitting select change from "'+elem[0].name+'"');
    				f.ajaxSubmit(opts);
    			}
    		});
    		var success_form = function(o,s,jform) {
    			$.djpcms.jsonCallBack(o,s,jform);
    			jform.css({'opacity':'1'});
    		};
    		$(cfg.selector_form,$this).each(function() {
    		    var f = $(this);
    		    var opts = {
    		            url:      	 this.action,
    		            type:     	 this.method,
    				   		success:  	 success_form,
    				   		submitkey: 	 config.post_view_key,
    				   		dataType:    "json",
    				   		beforeSubmit: presubmit_form};
    			f.ajaxForm(opts);
    			if(f.hasClass(config.autoload_class))  {
    				var name = f.attr("name");
    				f[0].clk = $(":submit[name='"+name+"']",f)[0];
    				f.ajaxSubmit(opts);
    			}
    		});
    	}
    });
    
    /**
     * Autocomplete Off
     */
    $.djpcms.decorator({
    	id:"autocomplete_off",
    	decorate: function($this,config) {
    		$('.autocomplete-off',$this).each(function() {
    			$(this).attr('autocomplete','off');
    		});
    		$('input:password',$this).each(function() {
    			$(this).attr('autocomplete','off');
    		});
    	}
    });
    
    /**
     * Classy Search
     */
    $.djpcms.decorator({
    	id:"classy-search",
    	decorate: function($this,config) {
    		$('.classy-search',$this).each(function() {
    			var el = $(this),
    			    val = el.val(),
    			    df = el.attr('title');
    			if(!val) {
    				el.val(df);
    			}
    			if(el.val() === df) {
    				el.addClass('idlefield');
    			}
    			el.focus(function() {
    					$(this).removeClass('idlefield').val('');
    			}).blur(function() {
    				$(this).addClass('idlefield');
    			});
    		});
    	}
    });
    
    /**
     * box decorator
     * Collappsable boxes
     */
    $.djpcms.decorator({
    	id:"djpcms_box",
    	description:"Decorate a DJPCMS box element",
    	decorate: function($this,config) {
    		var pselector = '.djpcms-html-box.collapsable',
    		    cname = pselector + ' a.collapse',
    		    bname = '.hd',
    		    elems;
    		$(cname,$this).mousedown(function (e) {
    			e.stopPropagation();    
    		}).click(function() {
    		    var self = $(this),
    		        span = $('span',this),
    		        cp = self.parents(pselector).first(),
    		        be = config.box_effect,
    		        bd = $('.bd',cp).first();
    			if(cp.hasClass('collapsed')) {
    				bd.show(be.type,{},be.duration,function(){
    				    cp.removeClass('collapsed');
    				    span.removeClass('ui-icon-circle-triangle-s')
    				        .addClass('ui-icon-circle-triangle-n');
    				});
    			}
    			else {
    				bd.hide(be.type,{},be.duration, function(){cp.addClass('collapsed');});
    				span.removeClass('ui-icon-circle-triangle-n')
                        .addClass('ui-icon-circle-triangle-s');
    			}
    			//cp.toggleClass('collapsed');
    			return false;
    		});
    	}
    });
    
    // Calendar Date Picker Decorator
    $.djpcms.decorator({
    	id:"datepicker",
    	config: {
            selector: 'input.dateinput',
            dateFormat: 'd M yy',
        },
    	decorate: function($this, config) {
    	    var opts = config.datepicker;
    		$(opts.selector,$this).datepicker(opts);
    	}
    });
    
    // Currency Input
    $.djpcms.decorator({
        id:"numeric",
        config: {
            selector: 'input.numeric',
            negative_class: 'negative'
        },
        format: function(elem,nc) {
            elem = $(elem);
            var v = $.djpcms.format_currency(elem.val());
            if(v.negative) {elem.addClass(nc);}
            else {elem.removeClass(nc);}
            elem.val(v.value); 
        },
        decorate: function($this, config) {
            var opts = config.numeric,
                format = this.format;
            $(opts.selector,$this).keyup(function() {
                format(this,opts.negative_class); 
            });
        }
    });
    
    /**
     * Cycle jQuery Plugin decorator, from django-flowrepo
     * 
     */ 
    $.djpcms.decorator({
    	id:"image_cycle",
    	decorate: function($this, config) {
    		if(!$.cycle) {
    			return;
    		}
    		$('.image-cycle', $this).each(function() {
    			var this_ = $(this);
    			var w     = this_.width();
    			var h     = this_.height();
    			var classes = this.className.split(" ");
    			var type_  = 'fade';
    			var speed_ = 5000;
    			var timeout_ = 10000;
    			$('img',this_).width(w).height(h);
    			$.each(classes,function(i,v) {
    				if(v.substr(0,6) === "speed-"){
    					try {
    						speed_ = parseInt(v.substr(6));
    					} catch(e) {}
    				}
    				else if(v.substr(0,8) === "timeout-"){
    					try {
    						timeout_ = parseInt(v.substr(8));
    					} catch(e2) {}
    				}
    				else if(v.substr(0,5) === "type-") {
    					type_ = v.substr(5);
    				}
                });
    			this_.cycle({fx: type_,
    					  speed: speed_,
    					  timeout: timeout_});
    		});
    	}
    });

    
    $.djpcms.decorator({
    	id: 'taboverride',
    	description: "Override tab key to insert n spaces",
    	config: {
    	 spaces: 4    
    	},
    	decorate: function($this,config) {
    		if($.fn.tabOverride) {
    			$.fn.tabOverride.setTabSize(config.taboverride.spaces);
    			$('textarea.taboverride',$this).tabOverride(true);
    		}
    	}
    });
    

    $.djpcms.addJsonCallBack({
        id: "autocomplete",
        handle: function(data, elem) {
            elem.response($.map(data, function( item ) {
                return {
                    value: item[0],
                    label: item[1],
                    real_value: item[2],
                    multiple: elem.multiple,
                }
            }));
        }
    });
    
    $.djpcms.decorator({
        id: 'asmSelect',
        config: {
            defaults: {
                addItemTarget: 'bottom',
                animate: true,
                highlight: true,
                sortable: false
            }
        },
        decorate: function($this,config) {
            $.each($('select[multiple="multiple"]',$this), function() {
                var v = $(this),
                    data = v.data(),
                    opts = data.options ? data.options : {},
                    options  = $.extend(true, {}, config.asmSelect.defaults, opts);
                v.bsmSelect(options);
            });
        }
    });
    
    
    $.djpcms.decorator({
        id:'message',
        config: {
            dismiss: true,
            fade: 400,
            float: 'right'
        },
        decorate: function($this,config) {
            var opts = config.message;
            $('li.messagelist, li.errorlist',$this).each(function(){
                var li = $(this),
                    a = $('<a><span class="ui-icon ui-icon-closethick"></span></a>')
                        .css({'float':opts.float})
                        .addClass('ui-corner-all')
                        .mouseenter(function(){$(this).addClass('ui-state-hover');})
                        .mouseleave(function(){$(this).removeClass('ui-state-hover');})
                        .click(function(){$(this).parent('li').fadeOut(opts.fade,'linear',function(){
                            $(this).remove();
                            });
                        });
                li.append(a);
            });
        }
    });  
    
    $.djpcms.decorator({
        id: "autocomplete",
        description: "Autocomplete to an input",
        config: {
            selector:'input.autocomplete',
            minLength: 2,
            maxRows: 50,
            separator: ', ',
        },
        decorate: function($this,config) {
            var opts = config.autocomplete;
            
            function split( val ) {
                return val.split( /,\s*/ );
            }
            
            function clean_data(terms,data) {
                new_data = [];
                $.each(terms,function(i,val) {
                    for(i=0;i<data.length;i+=1) {
                        if(data[i].label == val) {
                            new_data.push(data[i]);
                            break;
                        }
                    }
                });
                return new_data;
            }
            
            // The call back from from to obtain the real data
            function get_real_data(multiple,separator) {
                return function(val) {
                    if(multiple) {
                        var data = [];
                        $.each(clean_data(split(val),this.data),function(i,d) {
                            data.push(d.value);
                        });
                        return data.join(separator);
                    }
                    else {
                        if(val && this.data.length) {
                            return this.data[0].real_value;
                        }
                        else {
                            return '';
                        }
                    }
                }
            }
                
            $(opts.selector,$this).each(function() {
                var elem = $(this),
                    data = elem.data(),
                    url = data.url,
                    choices = data.choices,
                    maxRows = data.maxrows || opts.maxRows,
                    multiple = data.multiple,
                    separator = data.separator || opts.separator,
                    elemdata = {'get': get_real_data(multiple,separator),
                                'data': []},
                    initials,
                    options = {
                            minLength: data.minlength || opts.minLength,
                            select: function(event, ui) {
                                var item = ui.item,
                                    display = item.label,
                                    real_data = $.data(this,'real_value'),
                                    data = real_data['data'];
                                if(multiple) {
                                    var terms = split(this.value);
                                    terms.pop();
                                    data = clean_data(terms,data);
                                    terms.push(display);
                                    new_data.push(item);
                                    terms.push("");
                                    display = terms.join(separator);
                                }
                                else {
                                    data = [item];
                                }
                                real_data['data'] = data;
                                $.data(this,'real_value',real_data);
                                this.value = display;
                                return false;
                            }
                    };
                
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
                initials = $.data(this,'initial_value');
                if(initials) {
                    $.each(initials, function(i,initial) {
                        elemdata['data'].push({value:initial[0],
                                               label:initial[1]});
                    });
                }
                elem.data('real_value',elemdata);
                
                if(choices) {
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
                    options.source = function(request,response) {
                                    var ajax_data = {style: 'full',
                                                     maxRows: maxRows,
                                                     q: request.term
                                                     },
                                        loader = $.djpcms.ajax_loader(url,
                                                                    'autocomplete',
                                                                    'get',ajax_data),
                                        that = {'response':response,
                                                'multiple': multiple,
                                                'request':request};                                    
                                    $.proxy(loader,that)();
                                };
                    elem.autocomplete(options);
                }
            })
        }
    });
    
    
    $.djpcms.decorator({
    	id: "rearrange",
    	config: {
    	    body_selector: 'body.admin',
    	},
    	description: "Drag and drop functionalities in editing mode",
    	decorate: function($this,config) {
    		// The selectors
    	    if(!$(config.rearrange.body_selector).length) {
    	        if(!$.djpcms.content_edit) {
    	            return;
    	        }
    	    }
    	    $.djpcms.content_edit = (function() {
    	        
    	        var sortblock = '.sortable-block',
    	            divpaceholder = 'djpcms-placeholder',
    	            editblock = 'div.edit-block',
    	            columns = $(sortblock),
    	            holderelem = columns.commonAncestor(),
    	            curposition = null,
    	            logger = $.djpcms.logger;
    	        
    	        
    	        columns.delegate(editblock+'.movable .hd', 'mousedown', function(event) {
    	            curposition = position($(this).parent(editblock));
    	            $.djpcms.logger.info('selected item to move');
    	            var elem = $(this).parent();
                    elem.css({
                        width: elem.width() + 'px'
                    });
    	        });
    	        
    	        function position(elem) {
    	            var neighbour = elem.prev(editblock),
    	                data = {};
                    if(neighbour.length) {
                        data.previous = neighbour.attr('id');
                    }
                    else {
                        neighbour = elem.next(editblock);
                        if(neighbour.length) {
                            data.next = neighbour.attr('id');
                        }
                    }
                    return data;
    	        }
    	        
    			function moveblock(elem, pos, callback) {
    				var data = $.extend($.djpcms.ajaxparams('rearrange'),pos);
    				var form = $('form.djpcms-blockcontent',elem);
    				function movedone(e,s) {
    					$.djpcms.jsonCallBack(e,s);
    					callback();
    				}
    				if(form) {
    					var url = form.attr('action');
    					logger.info('Sending rearrange post request to "'+url+'"')
    					$.post(url,
    						   data,
    						   movedone,
    						   'json');
    				}
    			}
    		
    			columns.sortable({
    				items: editblock,
    				cancel: "div.edit-block:not(.movable)",
    				handle: 'div.hd',
    	            forcePlaceholderSize: true,
    	            connectWith: sortblock,
    				revert: 300,
    	            delay: 100,
    	            opacity: 0.8,
    	            containment: holderelem,
    	            placeholder: divpaceholder,
    	            start: function (e,ui) {
    	                $(ui.helper).addClass('dragging');
    	            },
    	            stop: function (e,ui) {
    	                var elem = ui.item;
    	                logger.info('Stopping drag and drop of element ' + elem);
    	                elem.css({width:''}).removeClass('dragging');
    	                function updatedone() {
    	                	columns.sortable('enable');
    	                }
    	                var pos = position(elem);
    	                if(pos.previous) {
    	                    if(pos.previous === curposition.previous) {return;}
    	                }
    	                else {
    	                    if(pos.next === curposition.next) {return;}
    	                }
    	                columns.sortable('disable');
    	                moveblock(elem,pos,updatedone);
    	            }
    			});
    	    }());
    	}
    });
    
    $.djpcms.decorator({
        id: "textselect",
        config: {
            selector: 'div.text-select select',
        },
        description: "A selct widget with text to display",
        decorate: function($this,config) {
            // The selectors
            function text(elem) {
                var me = $(elem),
                    pa = me.parent(),
                    val = me.val(),
                    el;
                $('.target',pa).hide();
                if(val) {
                    $('.target.'+val,pa).show();
                }
            }
            
            $(config.textselect.selector,$this).change(function(){text(this)});
        }
    });
    
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
    }
    
    
}(jQuery));
    
    
    
    (function($){ 		  
    	$.popupWindow = function(instanceSettings){
    		
    		var defaultSettings = {
    			centerBrowser:0, // center window over browser window? {1 (YES) or 0 (NO)}. overrides top and left
    		centerScreen:0, // center window over entire screen? {1 (YES) or 0 (NO)}. overrides top and left
    		height:500, // sets the height in pixels of the window.
    		left:0, // left position when the window appears.
    		location:0, // determines whether the address bar is displayed {1 (YES) or 0 (NO)}.
    		menubar:0, // determines whether the menu bar is displayed {1 (YES) or 0 (NO)}.
    		resizable:0, // whether the window can be resized {1 (YES) or 0 (NO)}. Can also be overloaded using resizable.
    		scrollbars:0, // determines whether scrollbars appear on the window {1 (YES) or 0 (NO)}.
    		status:0, // whether a status line appears at the bottom of the window {1 (YES) or 0 (NO)}.
    		width:500, // sets the width in pixels of the window.
    		windowName:null, // name of window set from the name attribute of the element that invokes the click
    		windowURL:null, // url used for the popup
    		top:0, // top position when the window appears.
    		toolbar:0 // determines whether a toolbar (includes the forward and back buttons) is displayed {1 (YES) or 0 (NO)}.
    	};
    	
    	settings = $.extend({}, defaultSettings, instanceSettings || {});
    	
    	var windowFeatures =    'height=' + settings.height +
    							',width=' + settings.width +
    							',toolbar=' + settings.toolbar +
    							',scrollbars=' + settings.scrollbars +
    							',status=' + settings.status + 
    							',resizable=' + settings.resizable +
    							',location=' + settings.location +
    							',menuBar=' + settings.menubar;
    
    	settings.windowName = this.name || settings.windowName;
    	var centeredY,centeredX;
    
    	if(settings.centerBrowser){
    			
    		if ($.browser.msie) {//hacked together for IE browsers
    			centeredY = (window.screenTop - 120) + ((((document.documentElement.clientHeight + 120)/2) - (settings.height/2)));
    			centeredX = window.screenLeft + ((((document.body.offsetWidth + 20)/2) - (settings.width/2)));
    		}else{
    			centeredY = window.screenY + (((window.outerHeight/2) - (settings.height/2)));
    			centeredX = window.screenX + (((window.outerWidth/2) - (settings.width/2)));
    		}
    		window.open(settings.windowURL, settings.windowName, windowFeatures+',left=' + centeredX +',top=' + centeredY).focus();
    	}else if(settings.centerScreen){
    		centeredY = (screen.height - settings.height)/2;
    		centeredX = (screen.width - settings.width)/2;
    		window.open(settings.windowURL, settings.windowName, windowFeatures+',left=' + centeredX +',top=' + centeredY).focus();
    	}else{
    		window.open(settings.windowURL, settings.windowName, windowFeatures+',left=' + settings.left +',top=' + settings.top).focus();	
    	}
    };
}(jQuery));
