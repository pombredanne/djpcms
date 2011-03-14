/*
 * File:         djpcms.js
 * Description:  djpcms Javascript Site Manager
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
        var parents = [],
            minlen = Infinity,
            j;

        $(this).each(function() {
            var curparents = $(this).parents();
            parents.push(curparents);
            minlen = Math.min(minlen, curparents.length);
        });

        $.each(parents, function(i,p) {
            parents[i] = p.slice(p.length - minlen);
        });

        // Iterate until equality is found
        $.each(parents[0], function(i,p) {
            var equal = true;
            for(j=0;j<parents.length;j++) {
                if(parents[j][i] !== p) {
                    equal = false;
                    break;
                }
            }
            if(equal) {
                return $(p);
            }
        });
        return $([]);
    };
	
    /**
     * djpcms site manager
     */
    $.djpcms = (function() {
        
        var decorators = {},
            jsonCallBacks = {},
            logging_pannel = null,
            inrequest = false,
            panel = null,
            defaults = {
		        media_url:		   "/media-site/",
    	        confirm_actions:{
    	            'delete': 'Please confirm delete',
    	            'flush': 'Please confirm flush'
    	                },
    	        autoload_class: "autoload",
    	        post_view_key: "xhr",
    	        ajax_server_error: "ajax-server-error",
    	        errorlist: "errorlist",
    	        formmessages: "form-messages",
    	        date_format: "d M yy",
    	        box_effect:		   {type:"blind",duration:500},
    	        remove_effect:	   {type:"drop",duration:500},
    	        bitly_key:		   null,
    	        twitter_user:	   null,
    	        fadetime:		   200,
    	        ajaxtimeout:	   30,
    	        //tabs:			   {cookie: {expiry: 7}},
    	        tablesorter:	   {widgets:['zebra','hovering']},
    	        debug:			   false
    	        };
		
		function set_logging_pannel(panel) {
			logging_pannel = panel;
		}
		
		function log(s) {
			if($.djpcms.options.debug) {
				if (typeof console !== "undefined" && typeof console.debug !== "undefined") {
					console.log('$.djpcms: '+ s);
					if(logging_pannel) {
						logging_pannel.prepend('<p>'+s+'</p>');
					}
				} 
			}
		}
		
		function _postparam(name) {
			var reqdata = {submitkey: defaults.post_view_key};
			if(name){
				reqdata[defaults.post_view_key] = name;
			}
			return reqdata;
		}
		
		// Set options
		function setOptions(options_) {
			$.extend(true, defaults, options_);
		}
		
		// Add a new decorator
		function addDecorator(deco) {
			decorators[deco.id] = deco.decorate;
			if(deco.config) {
                defaults[deco.id] = deco.config;
            }
		}
		
		// Add a new decorator
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
		        return jcb.handle(data.body, elem) & data.error;
		    }
		    else {
		        log('Could not find callback ' + id);
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
			var v;
			if(status === "success") {
				v = _jsonParse(data,elem);
			}
			else {
				v = false;
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
				var logger = $('.djp-logging-panel',me);
				if(logger) {
					set_logging_pannel(logger);
				}
				
				$.each(decorators,function(id,decorator) {
					log(me.toString() + ' - adding decorator ' + id);
					decorator(me,config);
				});						
			});
		}
		
		//    API
		return {
		    construct: _construct,
		    options: defaults,
		    jsonParse: _jsonParse,
		    'addJsonCallBack': addJsonCallBack,
		    jsonCallBack: _jsonCallBack,
		    decorator: addDecorator,
		    set_options: setOptions,
		    postparam: _postparam,
		    set_inrequest: function(v){inrequest=v;},
		    'inrequest': function(){return inrequest;},
		    'log': log,
		    'panel': function() {
		        // A floating panel
		        if(!panel) {
	                panel = $('<div>').hide().appendTo($('body'))
	                                .addClass('ui-widget ui-widget-content ui-corner-all')
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
	
	$.djpcms.errorDialog = function(html,title) {
	    title = title || 'Something did not work';
	    var el = $('<div title="'+title+'"></div>').html(html+'');
	    width = $.djpcms.smartwidth(html);
	            el.dialog({modal:true,
	                       dialogClass: 'ui-state-error',
	                       'width': width});
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
		handle: function(data, elem) {
			$.each(data, function(i,b) {
				var el = $(b.identifier,elem);
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
						if(b.type === 'addto') {
							el.html(el.html() + b.html);
						}
						else if(b.type === 'replacewith') {
							el.replaceWith(b.html);
						}
						else {
							el.html(b.html);
						}
						el.djpcms();
						el.show();
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
				if(el) {
					var be = $.djpcms.options.remove_effect;
					el.hide(be.type,{},be.duration,function() {el.remove();});
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
			var el = $('<div></div>').html(data.html);
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
							var extra = $.djpcms.postparam(b.func);
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
        id:'jquery-buttons',
        decorate: function(obj, config) {
           $('input[type="submit"]',obj).button();
           $('a.button').each(function() {
               var a = $(this),
                   sp = a.children('span'),
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
           });
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
	
    /**
     * Table-sorter decorator
     * decorate tables with jquery.tablesorter plugin
     * Plugin can be found at http://tablesorter.com/
     */
    $.djpcms.decorator({
        id:"tablesorter",
        decorate: function($this,config) {
            $('table.tablesorter',$this).each(function() {
                $(this).tablesorter(config.tablesorter);
            });
        }
    });
    
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
            fadetime: 500
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
		}
	});
	
	
	/**
	 * Ajax links, buttons and select 
	 */
    $.djpcms.decorator({
        id:	"ajax_widgets",
        description: "add ajax functionality to links, buttons and selects",
        decorate: function($this,config) {
            var ajaxclass = config.ajaxclass ? config.ajaxclass : 'ajax';
            var confirm = config.confirm_actions;
            
            function callback(o,s,e) {
                $.djpcms.jsonCallBack(o,s,e);
            }
            
            function sendrequest(elem,name) {
				var url = elem.attr('href');
				if(url) {
					var p = $.djpcms.postparam(name);
					$.post(url,
							$.param(p),
							callback,
							"json");
				}
			}
			function deco(event,elem) {
				event.preventDefault();
				if($.djpcms.inrequest()) {
					return;
				}
				$.djpcms.set_inrequest(true);
				var a = $(elem);
				var name = a.attr('name');
				var conf = confirm[name];
				if(conf) {
					var el = $('<div></div>').html(conf);
					el.dialog({modal: true,
							   draggable: false,
							   resizable: false,
							   buttons: {
								   Ok : function() {
									   $( this ).dialog( "close" );
									   sendrequest(a,name);
								   },
								   Cancel: function() {
									   $(this).dialog( "close" );
									   $.djpcms.set_inrequest(false);
								   }
						}});
				}
				else {
					sendrequest(a,name);
				}
			}
			$('a.'+ajaxclass,$this).click(function(event) {deco(event,this);});
			$('button.'+ajaxclass,$this).click(function(event) {deco(event,this);});
			$('select.'+ajaxclass,$this).change(function(event) {
				var a    = $(this);
				var _url = a.attr('href');
				var f    = a.parents('form');
				if(f.length === 1 && !_url) {
					_url = f.attr('action');
				}
				if(!_url) {
					_url = window.location.toString();
				}
				if(!f) {
					var p   = $.djpcms.postparam(a.attr('name'));
					p.value = a.val();
					$.post(_url,$.param(p),$.djpcms.jsonCallBack,"json");
				}
				else {
					var opts = {
							url:       _url,
							type:      'post',
							success:   callback,
							submitkey: config.post_view_key,
							dataType: "json"
							};
					f[0].clk = this;
					f.ajaxSubmit(opts);
				}
			});
			
			var presubmit_form = function(formData, jqForm, opts) {
				jqForm.css({'opacity':'0.5'});
				$('.'+config.errorlist+
				 ',.'+config.ajax_server_error,jqForm).fadeOut(100);
				return true;
			};
			var success_form = function(o,s,jform) {
				$.djpcms.jsonCallBack(o,s,jform);
				jform.css({'opacity':'1'});
			};
			$('form.'+ajaxclass,$this).each(function() {
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
				$(this).val('');
				$(this).attr('autocomplete','off');
			});
			$('input:password',$this).each(function() {
				$(this).val('').attr('autocomplete','off');
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
				var el = $(this);
				el.defaultValue = el.attr('title');
				if(!el.val()) {
					el.val(el.defaultValue);
				}
				if(el.val() == el.defaultValue) {
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
			var cname = 'djpcms-html-box';
			var bname = '.hd';
			var elems;
			if($this && $this.hasClass(cname)) {
				elems = $this;
			}
			else {
				elems = $('.'+cname,$this);
			}
			elems.each(function() {
				var el = $(this);
				if(el.hasClass('collapsable')) {
					var container = $(bname,el);
					if(container.length) {
						var link = $('a.collapse',container);
						if(link.length) {
							link.mousedown(function (e) {
								e.stopPropagation();    
							}).click(function() {
							    var self = $(this),
							        span = $('span',this),
							        cp = self.parents('.'+cname),
							        be = config.box_effect;
								if(cp.hasClass('collapsed')) {
									$('.bd',cp).show(be.type,{},be.duration,function(){
									    cp.removeClass('collapsed');
									    span.removeClass('ui-icon-circle-triangle-s')
									        .addClass('ui-icon-circle-triangle-n');
									});
								}
								else {
									$('.bd',cp).hide(be.type,{},be.duration, function(){cp.addClass('collapsed');});
									span.removeClass('ui-icon-circle-triangle-n')
                                        .addClass('ui-icon-circle-triangle-s');
								}
								//cp.toggleClass('collapsed');
								return false;
							});
						}
					}
				}
			});
		}
	});
	
	// Calendar Date Picker Decorator
	$.djpcms.decorator({
		id:"Date_Picker",
		decorate: function($this, config) {
			var ajaxclass = config.calendar_class ? config.calendar_class : 'dateinput';
			$('input.'+ajaxclass,$this).each(function() {
				$(this).datepicker({dateFormat: config.date_format});
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
					if(v.substr(0,6) == "speed-"){
						try {
							speed_ = parseInt(v.substr(6));
						} catch(e) {}
					}
					else if(v.substr(0,8) == "timeout-"){
						try {
							timeout_ = parseInt(v.substr(8));
						} catch(e) {}
					}
					else if(v.substr(0,5) == "type-") {
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
		id:"color_picker",
		decorate: function($this, config) {
			if(!$.fn.ColorPickerSetColor) {
				return;
			}
			$('input.color-picker', $this).each(function() {
				var div = $('<div class="color-picker"></div>');
				var iel = $(this).hide().after(div);
				var v = iel.val();
				div.append(iel.remove());
				div.css('backgroundColor', '#' + v);
				div.ColorPicker({
					onSubmit: function(hsb, hex, rgb, el) {
						var elem = $(el);
						$('input',elem).val(hex);
						elem.css('backgroundColor', '#' + hex);
						elem.ColorPickerHide();
					},
					onBeforeShow: function () {
						var v = $('input',this).val();
						$(this).ColorPickerSetColor(v);
					}
				});
			});
		}
	});
	
	$.djpcms.decorator({
		id:	"anchorbutton",
		description: "Decorate anchor as button using jQuery UI",
		decorate: function($this,config) {
			$('a.nice-button',$this).button();
		}
	});
	
	$.djpcms.decorator({
		id: 'taboverride',
		description: "Override tab key to insert 4 spaces",
		decorate: function($this,config) {
			if($.fn.tabOverride) {
				$.fn.tabOverride.setTabSize(4);
				$('textarea.taboverride',$this).tabOverride(true);
			}
		}
	});
	
	$.djpcms.decorator({
	    id:"uniforms",
	    config: {
	        tooltip:{x:10,y:30,effect:'clip',fadetime:200}
	    },
	    decorate: function($this,config) {
	        $('.uniForm .formHint',$this).each(function(){
	            var el = $(this);
	                c = config.uniforms,
	                html = el.html(),
	                label = $('label',el.parent());
	            if(label.length && html) {
	                $.data(label[0],'panel-html',html);
    	            label.css({cursor:'help'})
    	                 .mouseenter(function(e){
    	                     var t = c.tooltip,
    	                         p = $.djpcms.panel(),
        	                     x = e.pageX + c.tooltip.x,
        	                     y = e.pageY - c.tooltip.y,
        	                     text = $.data(this,'panel-html'),
        	                     width = $.djpcms.smartwidth(text),
    	                         height = p.width(width).html($.data(this,'panel-html')).height(),
    	                         y = Math.max(e.pageY - height - t.y,10);
        	                 p.css({'left':x,'top':y}).show(t.effect,{},t.fadetime);})
        	             .mouseleave(function() {
        	                 $.djpcms.panel().hide();
        	             });
	            }
	        });
	    }
	});
	
	$.djpcms.decorator({
		id:	"autocomplete",
		description: "add ajax autocomplete to an input",
		decorate: function($this,config) {
			$('.djp-autocomplete',$this).each(function() {
				var el = $(this);
				var display  = $('input.lookup',el).attr('autocomplete','off');
				var divo    = $('div.options',el);
				var url     = $('a',divo).attr('href');
				var sep		= $('span.separator',divo);
				var name	= $('span.name',divo);
				if(name.length) {
					display.attr('_lookup',name.html());
				}
				var inline  = false;
				if(sep.length) {
					sep = sep.html();
				}
				else {
					sep = ' ';
				}
				if($('span.inline',divo).length) {
					inline = true;
				}
				divo.remove();
				if(display && url) {
					var opts = 	{
						delay:10,
		                minChars:2,
		                matchSubset:1,
		                autoFill:false,
		                matchContains:1,
		                cacheLength:10,
		                selectFirst:true,
		                maxItemsToShow:10,
		                formatItem: function(data, i, total) {
		        			return data[1];
		        		}
					};
					if(display.hasClass('multi')) {
						opts.multiple = true;
						opts.multipleSeparator = sep || " ";
						if(!inline) {
							el.mousedown(function (e) {
								e.stopPropagation();    
							}).mouseup(function(e) {
								var originalElement = e.originalTarget || e.srcElement;
								try {
									var al = $(originalElement);
									if(al.hasClass('deletable')) {
										al.parent().remove();
									}
								} catch(err) {}
							});
						}
					}
					display.autocomplete(url, opts);
					display.bind("result", function(el,data,bo) {
						var me   = $(this);
						var name = me.attr("_lookup");
						var next = me.next();
						var v    = data[2];
						if(me.hasClass("multi")) {
							var lbl = data[0];
							if(inline) {
								//me.val(me.val() + lbl);
							}
							else {
								var td  = $('<div class="to_delete"><input type="hidden" name="'+name+'" value="'+v+'"/><a href="#" class="deletable"></a>'+lbl+'</div>');
								next.append(td);
								me.val("");
							}
						}
						else {
							next.val(v);
						}
					});
				}
			});
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
		            curposition = null;
		        
		        
		        columns.delegate(editblock+'.movable .hd', 'mousedown', function(event) {
		            curposition = position($(this).parent(editblock));
		            $.djpcms.log('selected item to move');
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
    				var data = $.extend($.djpcms.postparam('rearrange'),pos);
    				var form = $('form.djpcms-blockcontent',elem);
    				function movedone(e,s) {
    					$.djpcms.jsonCallBack(e,s);
    					callback();
    				}
    				if(form) {
    					var url = form.attr('action');
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
    	                elem.css({width:''}).removeClass('dragging');
    	                function updatedone() {
    	                	columns.sortable('enable');
    	                }
    	                var pos = position(elem);
    	                if(pos.previous) {
    	                    if(pos.previous == curposition.previous) {return;}
    	                }
    	                else {
    	                    if(pos.next == curposition.next) {return;}
    	                }
    	                columns.sortable('disable');
    	                moveblock(ui.item,pos,updatedone);
    	            }
    			});
		    }());
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
		var c = parseFloat(s);
		if(isNaN(c))  {
			return {value:s,negative:false};
		}
		isneg = false;
		if(c<0) {
			isneg = true;
			c     = Math.abs(c);
		}
		var cn  = parseInt(c,10);
		var de  = c - cn;
		if(de > 0) {
			var mul = Math.pow(10,precision);
			var atom = c/mul;
			if(atom > de)  {
				de = "";
			}
			else {
				atom += "";
				atom  = atom.split(".")[1];
				for(var i=0;atom.length;i++)  {
					if(parseInt(atom[i],10) > 0)  {
						break;
					}
				}
				mul = Math.pow(10,i+1);
				de  = parseFloat(parseInt(de*mul,10))/mul;
				ro  = "" + cn + de;
				ro  = ro.split(".");
				de  = "."+ro[1];
			}
		}
		else {
			de = "";
		}
		cn += "";
		var d,k;
		var N  = cn.length;
		var cs = "";
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
