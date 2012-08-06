
module("multiselect: core");


function createSelect () {
    var ms = $('<select multiple="multiple">');
    for (i = 1; i <= 10; ++i) {
        ms.append($('<option>', {value: 'value' + String(i), html: 'text' + String(i)}));
    }
    return ms;
}

test('widget', function () {
    expect(3);
    var ms = $.djpcms.widgets.multiSelect;
    equal(ms.name, 'multiSelect');
    equal(ms.selector, 'select[multiple="multiple"]');
    ok(ms.plugins);
});


test('create', function () {
    var se = createSelect(),
        ms = $.djpcms.ui.multiSelect(se);

});