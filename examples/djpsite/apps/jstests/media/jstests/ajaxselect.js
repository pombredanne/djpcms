
module("ajaxselect");

function someoptions(count) {
    var opts = [], count = count || 10, i;
    for(i=0;i<count;i++) {
        opts.push({value:i,text:'option ' + (i+1)});
    }
    return opts;
}

function create_select(options) {
    var cols = cols || 5,
        rows = rows || 20,
        options = options || someoptions(),
        se = $('<select class="ajax" data-href="/getdata/" data-table-name="path"/>');
        el = $('#testcontainer').html('').append(se);
        $.each(options,function(i,o) {
            se.append(new Option(o.text,o.value));
        });
    return se;
}


