
module("jQuery-Functionalities");

(function ($) {
    
    function data_element(options) {
        var el = $('<div>');
        $.each(options, function(key,val) {
            el.attr('data-'+key,val);
        });
        return el;
    }
    
    test("Extra data", function() {
        var el = data_element({'href':'/getdata/',
                               table: '["ciao",3]',
                               obj: '{"name": "path", "rows": 2}'}),
            data = el.data();
        ok(data.href === '/getdata/', "Correct href data");
        ok($.isArray(data.table), "Correct array data");
        ok(data.table[0] === "ciao","Correct array value");
        ok(data.table[1] === 3,"Correct array value 2");
        ok(data.obj.name === 'path',"Correct object value");
        ok(data.obj.rows === 2,"Correct object value 2");
    });
    
}(jQuery))