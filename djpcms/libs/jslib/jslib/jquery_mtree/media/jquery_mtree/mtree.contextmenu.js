/**
 * Add a Context Menu to the tree. Requires the djpkit plugin.
 */
(function ($) {

    $.mtree.plugin("contextmenu", {
        defaults : { 
            select_node : false, // requires UI plugin
            show_at_node : true,
            items : []
        },
        init_instance : function () {
    		this.container()
    			.delegate("a", "contextmenu.mtree", $.proxy(function (e) {
    				e.preventDefault();
    				this.show_contextmenu(e.currentTarget, e.pageX, e.pageY);
    			},this))
    			.bind("destroy.mtree", $.proxy(function () {
					if(this.data.contextmenu) {
						$.djpkit.context.hide();
					}
				}, this));
    	},
        extensions: {
    		show_contextmenu : function (obj, x, y) {
    			obj = this.node(obj);
    			var s = this.settings().contextmenu,
    				a = obj.children("a:visible:eq(0)"),
    				o = false,
    				context = $.djpkit.context;
    			if(s.select_node && this.data.ui && !this.is_selected(obj)) {
    				this.deselect_all();
    				this.select_node(obj, true);
    			}
    			if(s.show_at_node || typeof x === "undefined" || typeof y === "undefined") {
    				o = a.offset();
    				x = o.left;
    				y = o.top + this.data.core.li_height;
    			}
    			if($.isFunction(s.items)) { s.items = s.items.call(this, obj); }
    			this.data.contextmenu = true;
    			this.logger().info('Show context menu at ('+x+','+y+')');
    			context.show(s.items, a, x, y, this, obj);
    		}
    	}
    });
    
})(jQuery);
