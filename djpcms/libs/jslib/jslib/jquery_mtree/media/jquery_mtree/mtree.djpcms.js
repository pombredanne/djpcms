/**
 * Decorator for djpcms
 */
/*jslint browser: true, onevar: true, undef: true, bitwise: true, strict: true */
/*global jQuery */
(function ($) {
    "use strict";
    
    if($.mtree && $.djpcms) {
        
        /**
         * Received data from server
         */
        $.djpcms.addJsonCallBack({
            id: "mtree-data",
            handle: function(data, elem) {
                elem.parse_json(-1,data);
            }
        });
        
        /**
         * Error handler from server
         */
        $.djpcms.addJsonCallBack({
            id: "mtree-error",
            handle: function(msg, action) {
                var inst = action.inst,
                    rlbk = action.rlbk;
                if(inst) {
                    inst.logger().error(msg);
                }
                else {
                    $.djpcms.errorDialog(msg);
                }
                if(rlbk) {
                    $.mtree.rollback(action.rlbk);
                }
            }
        });
        
        
        $.djpcms.decorator({
            'id':'mtree',
            description: "Apply mupltiple tree plugin to an element",
            decorate: function($this,config) {
                $('.mtree',$this).each(function() {
                    var elem = $(this),
                        opts = elem.data(),
                        url = opts.json.url,
                        action = $.djpcms.getAction('mtree',elem.attr('id'));
                    opts.logger = $.djpcms.logger;
                    opts.json.url = $.djpcms.ajax_loader(url,'reload');
                    // If an action is registered perform it!
                    if(action) {
                        opts = action(opts);
                    }
                    elem.mtree(opts);
                });
            }
        });
        
    }
    
}(jQuery));
