/* 
 * mtree ui plugin 1.0
 * This plugins handles selecting/deselecting/hovering/dehovering nodes
 */
/*global jQuery */
"use strict";
(function ($) {
	$.mtree.plugin("ui", {
		is_default: true,
		defaults : {
			select_limit : -1, // 0, 1, 2 ... or -1 for unlimited
			select_multiple_modifier : "ctrl", // on, or ctrl, shift, alt
			selected_parent_close : "select_parent", // false, "deselect", "select_parent"
			select_prev_on_delete : true,
			disable_selecting_children : false,
			initially_select : [],
			class_default: '',
			class_hover: 'ui-state-hover',
			class_active: 'ui-state-highlight'
		},
		init_instance : function () {
			var ui = this.data.ui,
				settings = this.settings().ui;
			ui.class_hover = settings.class_hover;
			ui.class_active = settings.class_active;
			ui.class_default = settings.class_default;
			ui.selected = $(); 
			ui.last_selected = false; 
			ui.hovered = null;
			ui.to_select = settings.initially_select;

			this.container()
				.delegate("a", "click.mtree", $.proxy(function (event) {
						event.preventDefault();
						this.select_node(event.currentTarget, true, event);
					}, this))
				.delegate("a", "mouseenter.mtree", $.proxy(function (event) {
						this.hover_node(event.target);
					}, this))
				.delegate("a", "mouseleave.mtree", $.proxy(function (event) {
						this.dehover_node(event.target);
					}, this))
				.bind("reopen.mtree", $.proxy(function () { 
						this.reselect();
					}, this))
				.bind("get_rollback.mtree", $.proxy(function () { 
						this.dehover_node();
						this.save_selected();
					}, this))
				.bind("set_rollback.mtree", $.proxy(function () { 
						this.reselect();
					}, this))
				.bind("close_node.mtree", $.proxy(function (event, data) { 
					var sel = settings.selected_parent_close,
						obj = this.node(data.rslt.obj),
						clk = (obj && obj.length) ? obj.children("ul").find("."+settings.class_active) : $(),
							_this = this;
						if(sel === false || !clk.length) { return; }
						clk.each(function () { 
							_this.deselect_node(this);
							if(sel === "select_parent") { _this.select_node(obj); }
						});
					}, this))
				.bind("delete_node.mtree", $.proxy(function (event, data) { 
						var sel = settings.select_prev_on_delete,
							obj = this.node(data.rslt.obj),
							clk = (obj && obj.length) ? obj.find("."+settings.class_active) : [],
							_this = this;
						clk.each(function () { _this.deselect_node(this); });
						if(sel && clk.length) { this.select_node(data.rslt.prev); }
					}, this))
				.bind("move_node.mtree", $.proxy(function (event, data) { 
						if(data.rslt.cy) { 
							data.rslt.oc.find("."+settings.class_active).removeClass(settings.class_active);
						}
					}, this));
		},
		extensions : { 
			_node : function (obj, allow_multiple) {
				if(typeof obj === "undefined" || obj === null) {
					return allow_multiple ? this.data.ui.selected : this.data.ui.last_selected;
				}
				return this.__super(obj);
			},
			save_selected : function () {
				var _this = this;
				this.data.ui.to_select = [];
				this.data.ui.selected.each(function () { _this.data.ui.to_select.push("#" + this.id.toString().replace(/^#/,"").replace('\\/','/').replace('/','\\/')); });
				this.__callback(this.data.ui.to_select);
			},
			reselect : function () {
				var _this = this,
					s = this.data.ui.to_select;
				s = $.map($.makeArray(s), function (n) { return "#" + n.toString().replace(/^#/,"").replace('\\/','/').replace('/','\\/'); });
				this.deselect_all();
				$.each(s, function (i, val) { if(val && val !== "#") { _this.select_node(val); } });
				this.__callback();
			},
			refresh : function (obj) {
				this.save_selected();
				return this.__call_old();
			},
			hover_node : function (obj) {
				var ui = this.data.ui;
				obj = this.node(obj);
				if(!obj.length) { return false; }
				if(ui.hovered !== obj) {
					this.dehover_node();
					ui.hovered = obj.children("a").addClass(ui.class_hover).removeClass(ui.class_default).parent();
					this.__callback({ "obj" : obj });
				}
			},
			dehover_node : function () {
				var ui = this.data.ui,
					obj = ui.hovered,
					p;
				if(!obj || !obj.length) { return false; }
				p = obj.children("a").removeClass(ui.class_hover).addClass(ui.class_default).parent();
				if(ui.hovered[0] === p[0]) { ui.hovered = null; }
				this.__callback({ "obj" : obj });
			},
			select_node : function (obj, check, e) {
				obj = this.node(obj);
				if(obj == -1 || !obj || !obj.length) { return false; }
				var settings = this.settings().ui,
					ui = this.data.ui,
					is_multiple = (settings.select_multiple_modifier == "on" ||
							(settings.select_multiple_modifier !== false && e && e[settings.select_multiple_modifier + "Key"])),
					is_selected = this.is_selected(obj),
					proceed = true;
				if(check) {
					if(settings.disable_selecting_children && is_multiple && obj.parents("li", this.container()).children("."+settings.class_active).length) {
						return false;
					}
					proceed = false;
					if(!is_multiple) {
						if (!is_selected) { 
							if(settings.select_limit == -1 || settings.select_limit > 0) {
								this.deselect_all();
								proceed = true;
							}
						}
					}
					else {
						if(is_selected) { 
							this.deselect_node(obj);
						}
						else if(settings.select_limit == -1 || ui.selected.length + 1 <= settings.select_limit) {
							proceed = true;
						}
					}
				}
				if(proceed && !is_selected) {
					obj.children("a").addClass(ui.class_active);
					ui.selected = ui.selected.add(obj);
					ui.last_selected = obj;
					this.__callback({ "obj" : obj });
				}
			},
			deselect_node : function (obj) {
				var ui = this.data.ui;
				obj = this.node(obj);
				if(!obj.length) { return false; }
				if(this.is_selected(obj)) {
					obj.children("a").removeClass(ui.class_active).addClass(ui.class_default);
					this.data.ui.selected = this.data.ui.selected.not(obj);
					if(this.data.ui.last_selected.get(0) === obj.get(0)) { this.data.ui.last_selected = this.data.ui.selected.eq(0); }
					this.__callback({ "obj" : obj });
				}
			},
			_toggle_select : function (obj) {
				obj = this.node(obj);
				if(!obj.length) { return false; }
				if(this.is_selected(obj)) { this.deselect_node(obj); }
				else { this.select_node(obj); }
			},
			_is_selected : function (obj) {
				return this.data.ui.selected.index(this.node(obj)) >= 0;
			},
			_get_selected : function (context) { 
				return context ? $(context).find("."+this.data.ui.class_active).parent() : this.data.ui.selected; 
			},
			deselect_all : function (context) {
				var clk = this.data.ui.class_active;
				if(context) { $(context).find("."+clk).removeClass(clk); } 
				else { this.container().find("."+clk).removeClass(clk); }
				this.data.ui.selected = $();
				this.data.ui.last_selected = false;
				this.__callback();
			}
		}
	});
}(jQuery));

