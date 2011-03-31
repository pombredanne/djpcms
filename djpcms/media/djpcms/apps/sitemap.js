
(function($) {
    
    if($.djpcms && $.mtree) {
        
        $.djpcms.addJsonCallBack({
            id: "tree-data",
            handle: function(data, elem) {
                elem.parse_json(-1,data);
            }
        });
        
        /**
         * Error handler from server
         */
        $.djpcms.addJsonCallBack({
            id: "tree-error",
            handle: function(msg, action) {
                var inst = action.inst,
                    rlbk = action.rlbk;
                if(inst) {
                    inst.logger().error(msg);
                }
                else {
                    $.djpcms.errorDialog(msp);
                }
                if(rlbk) {
                    $.mtree.rollback(action.rlbk);
                }
            }
        });
        
        $.djpcms.sitemap = function(selector,url) {
           
            $.djpcms.queue(function () {
                
                /**
                 * Load sitemap from server
                 */
                function sitemap_loader() {
                    var that = this;         };
                    $.ajax({'url':url,
                            type: 'post',
                            dataType: 'json',
                            success: function(e,s) {$.djpcms.jsonCallBack(e,s,that);},
                            data: $.djpcms.ajaxparams('reload')
                    });
                }
                
                $(selector).mtree({
                    "logger": $.djpcms.logger,
                    plugins: ['core','json','crrm','ui','table'],
                    json: {"url":sitemap_loader},
                    table: {min_height: '500px', name: 'path'}
                });
            });
        }
    }
}(jQuery));