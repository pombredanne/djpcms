

(function($) {
    /**
     * DJPCMS Decorator for Econometric ploting
     */
    if($.djpcms && $.fn.dataTable) {
        $.djpcms.decorator({
            id:"datatable",
            config: {
                selector: 'div.data-table',
                bJQueryUI: true,
                bProcessing: true,
                bServerSide: true,
                sAjaxSource: '.',
                widgets:['zebra','hovering','toolbox'],
                "aaSorting": [],
                "fnServerData": function ( sSource, aoData, fnCallback ) {
                    $.ajax({
                        "dataType": 'json', 
                        "type": "GET", 
                        "url": sSource, 
                        "data": aoData, 
                        "success": $.djpcms.jsonCallBack
                    });
                }
            },
            decorate: function($this,config) {
                var opts = config.datatable,
                    tbl = $(opts.selector);
                $.each($(opts.selector,$this),function() {
                    var elem = $(this),
                        tbl = $('table',elem)
                        data = elem.data('options') || {};
                    if(tbl.length == 1) {
                        opts = $.extend(true,data,opts)
                        tbl.dataTable(opts);
                    }
                });
            } 
        });
    }
}(jQuery));