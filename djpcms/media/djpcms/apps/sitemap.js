
(function($) {
    
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
        
        if(!$.mtree) {return;}
        
        function sitemap_loader() {
            
            function callBack(e,s) {
                $.djpcms.jsonCallBack(e,s,that);
            }
            
            var that = this,
                opts = {
                        'url':url,
                        type: 'post',
                        dataType: 'json',
                        success:   callBack,
                        data: $.djpcms.postparam('reload')
                        };
               
            $.ajax(opts);  
        }
        
        $(selector).mtree({
            plugins: ['core','json','crrm','ui','table'],
            json: {"url":sitemap_loader},
            table: {min_height: '500px'}
        });
    }
    
}(jQuery));