/* 
 * Handles creating/renaming/removing/moving nodes by user interaction.
 */
(function ($) {
	$.mtree.plugin("crrm", {
		is_default: true,
        defaults : {
            input_width_limit : 200,
            canmove: function(obj,ref) { return true; },
            always_copy: false, // false, true or "multitree"
            open_onmove: true,
            default_position: function(m) { return "last"; },
        },
		extensions : {
		    //
		    // Display an input element in the page.
		    // requires djpkit for handling floating element
			_show_input : function (obj, callback) {
				obj = this.node(obj);
				var el = obj.children('a'),
				    old_name = this.get_text(obj);
				    commit = $.proxy(function(name) {
                        if(name === "") { name = old_name; }
                        this.set_text(obj,name);
                        if(callback) {
                            callback({"obj" : obj,
                                      "new_name" : name,
                                      "old_name" : old_name});
                        }
                    }, this);
				$.djpkit.input.show(el, {val: old_name, callback: commit});
				this.set_text(obj, "");
			},
			//
			// Rename a new node
			rename : function (obj) {
				obj = this.node(obj);
				var that = this,
				    f = this.__callback;
				this.__rollback();
				this.show_input(obj, function(data) { 
					f.call(that,data);
				});
			},
			create : function (obj, position, js, callback, skip_rename) {
				var t, that = this;
				obj = this.node(obj);
				if(!obj) { obj = -1; }
				t = this.create_node(obj, position, js, function (t) {
					var p = this.parent(t),
						pos = $(t).index();
					if(callback) { callback.call(this, t); }
					if(p.length && p.hasClass("mtree-closed")) { this.open_node(p, false, true); }
					if(!skip_rename) { 
						this.show_input(t, function (obj, new_name, old_name) { 
							that.__callback({ "obj" : obj, "name" : new_name, "parent" : p, "position" : pos });
						});
					}
					else {
					    that.__callback({ "obj" : t, "name" : this.get_text(t), "parent" : p, "position" : pos });
					}
				});
				return t;
			},
			remove : function (obj) {
				this.delete_node(obj);
			},
			//
			// Move node. If succesful return true otherwise return false
			move_node : function (obj, target, position, is_copy) {
				var crrm = this.settings().crrm,
				    ul;
				is_copy = is_copy || false;
				if(obj[0] === target[0] || !crrm.canmove.call(this,obj,target)) {
				    return false;
				} 
				if(!position) {
				    position = crrm.default_position(obj);
				}
				if(crrm.always_copy === true || (crrm.always_copy === "multitree" && obj.rt.get_index() !== obj.ot.get_index() )) {
					is_copy = true;
				}
				this.set_opened(target);
				this.insert_node(obj, target, position, this.__callback);
				return !is_copy;
			},
			cut : function (obj) {
				obj = this.node(obj);
				this.data.crrm.cp_nodes = false;
				this.data.crrm.ct_nodes = false;
				if(!obj || !obj.length) { return false; }
				this.data.crrm.ct_nodes = obj;
			},
			copy : function (obj) {
				obj = this.node(obj);
				this.data.crrm.cp_nodes = false;
				this.data.crrm.ct_nodes = false;
				if(!obj || !obj.length) { return false; }
				this.data.crrm.cp_nodes = obj;
			},
			paste : function (obj) { 
				obj = this.node(obj);
				if(!obj || !obj.length) { return false; }
				if(!this.data.crrm.ct_nodes && !this.data.crrm.cp_nodes) { return false; }
				if(this.data.crrm.ct_nodes) { this.move_node(this.data.crrm.ct_nodes, obj); }
				if(this.data.crrm.cp_nodes) { this.move_node(this.data.crrm.cp_nodes, obj, false, true); }
				this.data.crrm.cp_nodes = false;
				this.data.crrm.ct_nodes = false;
			}
		}
	});
})(jQuery);