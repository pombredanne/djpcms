/**
 * Drag & Drop functionality.
 * Complements the CRRM plugin
 * 
 * @requires jQuery-UI
 */
(function ($) {
		
	$.mtree.plugin("dnd", {
	    defaults: {
	        opacity: 0.7
	    },
		init_instance : function () {
		    var self = this.container(),
		        dnd = this.settings().dnd,
		        crrm = this.settings().crrm;
		    
		    self.sortable({
		        items: 'a',
		        opacity: dnd.opacity,
		        placeholder: dnd.placeholder,
		        start: $.proxy(function(e, ui) {
		            var item = ui.item,
		                obj = this.node(item);
		            if(!crrm.canmove.call(this,obj)) {
		                item.sortable('cancel');
		                return;
		            }
		            this.data.dnd.dragging = obj;
		            $('<span class="dummy-node">'+item.html()+'</span>')
		                  .insertAfter(obj.children('ins'))
		                  .width(item.width())
		                  .height(item.height())
		                  .fadeTo(10,dnd.opacity);
		        },this),
		        stop: $.proxy(function(e, ui) {
		            var item = ui.item,
                        obj = this.node(item),
                        moving = this.data.dnd.dragging;
		            this.data.dnd.dragging = null;
		            $("span.dummy-node",moving).remove();
		            item.insertAfter(moving.children('ins'));
		            if(!this.move_node(moving,obj)) {
		                item.sortable('cancel');
		            }
                },this)
		    });
		},
	    extensions: {}
	});

}(jQuery));
