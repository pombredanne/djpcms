/*
 * File:         djpcms.js
 * Version:      0.4
 * Description:  djpcms Javascript Site Manager
 * Author:       Luca Sbardella
 * Language:     Javascript
 * License:      new BSD licence
 * repository:	 http://code.google.com/p/djpcms/
 * Organization: Dynamic Quant Limited
 * Contact:      luca.sbardella@gmail.com
 * @requires:	 jQuery, jQueryUI
 * 
 * Copyright (c) 2009, Luca Sbardella
 * New BSD License 
 * http://www.opensource.org/licenses/bsd-license.php
 *
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
	$.extend({
		djpcms: new function() { 
		
			var decorators = [];
			var jsonCallBacks = {};
	
			this.options = {
				media_url:		   "/media-site/",
				autoload_class:	   "autoload",
				ajax_server_error: "ajax-server-error",
				errorlist:		   "errorlist",
				formmessages:	   "form-messages",
				bitly_key:		   null,
				twitter_user:	   null,
				fadetime:		   200,
				ajaxtimeout:	   30,
				tablesorter:	   {},
				debug:			   false
			};
			
			this.postparam = function(name) {
				var reqdata = {submitkey: this.options.post_view_key};
				if(name){
					reqdata[this.options.post_view_key] = name;
				}
				return reqdata;
			};
			
			// Set options
			this.set_options = function(options_) {
				$.extend(true, this.options, options_);
			};
			
			// Add a new decorator
			this.addDecorator = function(decorator) {
				decorators.push(decorator);
			};
			// Add a new decorator
			this.addJsonCallBack = function(jcb) {
				jsonCallBacks[jcb.id] = jcb;
			};
			
			// Remove a decorator
			this.removeDecorator = function(id) {
				var ndecos = [];
				$.each(decorators,function(n,decorator) {
					if(decorator.id != id) {
						ndecos.push(decorator);
					}
				});
				this.decorators = ndecos;
			};
			
			/**
			 * Handle a JSON call back by looping through all the callback objects registered
			 * @param data JSON object
			 * @param el (Optional) jQuery object or HTMLObject
			 * @return boolean, true if everything is good, false if an error has occured
			 */
			this.jsonCallBack = function(data, status, elem) {
				if(status == "success") {
					var id  = data.header;
					var jcb = jsonCallBacks[id];
					if(jcb) {
						return jcb.handle(data.body, elem) & data.error;
					}
				}
			};
	
			this.construct = function() {
				return this.each(function() {
					var config = $.djpcms.options;
					
					// store common expression for speed					
					var $this = $(this);
					
					$.each(decorators,function(n,decorator) {
						decorator.decorate($this,config);
					});
				});
			};
		}
	});
	
	// extend plugin scope
	$.fn.extend({
        djpcms: $.djpcms.construct
	});
	
	
	var dj = $.djpcms;
	
	
	/**
	 * SERVER ERROR callback
	 */
	dj.addJsonCallBack({
		id: "servererror",
		handle: function(data, elem) {
			var el = $("<div></div>").html(data);
			el.dialog({modal:true});
		}
	});
	
	/**
	 * html JSON callback
	 */
	dj.addJsonCallBack({
		id: "htmls",
		handle: function(data, elem) {
			$.each(data, function(i,b) {
				var el = $(b.identifier,elem);
				if(!el.length & b.alldocument) {
					el = $(b.identifier);
				}
				if(el) {
					el.html(b.html);
					//if(b.type == "replace") {
					//	el.html(nel);
					//}
					//else {
					//	el.html(el.html() + nel);
					//}
					el.djpcms();
					el.show();
				}
			});
			return true;
		}
	});
	
	/**
	 * Remove html tags
	 */
	dj.addJsonCallBack({
		id: "remove",
		handle: function(data, elem) {
			$.each(data, function(i,b) {
				var el = $(b.identifier,elem);
				if(!el.length & b.alldocument) {
					el = $(b.identifier);
				}
				if(el) {
					el.fadeOut($.djpcms.options.fadetime,el.remove());
				}
			});
			return true;
		}
	});
	
	/**
	 * Redirect
	 */
	dj.addJsonCallBack({
		id: "redirect",
		handle: function(data, elem) {
			window.location = data;
		}
	});
	
	/**
	 * Dialog callback
	 * 
	 * Create a jQuery dialog from JSON data
	 */
	dj.addJsonCallBack({
		id: "dialog",
		handle: function(data, elem) {
			var el = $('<div></div>').html(data.html);
			var buttons = {};
			$.each(data.buttons,function(n,b) {
				buttons[b.name] = function() {
					b.d = $(this);
					
					b.dialogcallBack = function(data) {
						$.djpcms.jsonCallBack(data,el);
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
	
	
	/**
	 * Ajax links, buttons and select 
	 */
	dj.addDecorator({
		id:	"ajax-widgets",
		description: "add ajax functionality to links, buttons and selects",
		decorate: function($this,config) {
			var ajaxclass = config.ajaxclass ? config.ajaxclass : 'ajax';
			function deco(event,elem) {
				event.preventDefault();
				var a = $(elem);
				var url = a.attr('href');
				var p = $.djpcms.postparam(a.attr('name'));
				if(url) {
					$.post(url,$.param(p),$.djpcms.jsonCallBack,"json");
				}
			}
			$('a.'+ajaxclass,$this).click(function(event) {deco(event,this);});
			$('button.'+ajaxclass,$this).click(function(event) {deco(event,this);});
			$('select.'+ajaxclass,$this).change(function(event) {
				var a    = $(this);
				var _url = a.attr('href');
				var f    = a.parents('form');
				if(f.length == 1 && !_url) {
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
							success:   $.djpcms.jsonCallBack,
							submitkey: config.post_view_key,
							dataType: "json",
							};
					f[0].clk = this;
					f.ajaxSubmit(opts);
				}
			});
			
			var presubmit_form = function(formData, jqForm, opts) {
				jqForm.css({'opacity':'0.5'});
				$('.'+config.errorlist+
				 ',.'+config.ajax_server_error+
				 ',.'+config.formmessages,jqForm).fadeOut(100);
				return true;
			};
			var success_form = function(o,s,jform) {
				$.djpcms.jsonCallBack(o,s,jform);
				jform.css({'opacity':'1'});
			};
			$('form.'+ajaxclass,$this).each(function() {
				var f = $(this);
				var opts = {url:      	 this.action,
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
	 * box decorator
	 * 
	 */
	/*
	dj.addDecorator({
		id:"djpcms-box",
		decorate: function($this,config) {
			$('.djpcms-html-box',$this).each(function() {
				var el = $(this);
				if(el.hasClass('rounded')) {
					el.addClass('ui-corner-all');
				}
			});
		}
	});
	*/
	
	
	/**
	 * Accordion menu
	 */
	dj.addDecorator({
		id:"accordion-menu",
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
	});
	
	
	/**
	 * Table-sorter decorator
	 * decorate tables with jquery.tablesorter plugin
	 * Plugin can be found at http://tablesorter.com/
	 */
	dj.addDecorator({
		id:"tablesorter",
		decorate: function($this,config) {
			$('table.tablesorter',$this).each(function() {
				$(this).tablesorter(config.tablesorter);
			});
		}
	});
	
	
	// Calendar Date Picker Decorator
	dj.addDecorator({
		id:"Date-Picker",
		decorate: function($this, config) {
			$('.calendar-input',$this).each(function() {
				$(this).datepicker();
			});
		}
	});
	
	
})(jQuery);
