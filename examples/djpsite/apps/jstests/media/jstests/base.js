module("djpcms");

test("global object", function () {
    expect(3);
    ok($.djpcms);
    ok($.djpcms.options);
    ok($.djpcms.ui);
});


module("input: core");

test('classes', function () {
    expect(2);
    var ui = $.djpcms.ui,
        el = ui.input(),
        elem = el.element;
    ok(!elem.hasClass(el.config.classes.input));
    ok(el.wrapper.hasClass(el.config.classes.input));
});

module("button: core");

test('widget', function () {
    expect(4);
    var ui = $.djpcms.ui,
        btn1,
        btn2,
        elem;
    ok( ui.button, "button constructor available");
    btn1 = ui.button();
    ok( btn1.id >= 0, "First button created");
    equal( btn1.type, 'button', "Button is a button element");
    elem = btn1.element;
    btn2 = ui.button();
    equal( btn1.id + 1, btn2.id, "Second button created");
});

module("button: options");

test('text', function () {
    expect(2);
    var ui = $.djpcms.ui,
        btn1 = ui.button({text: 'ciao'}),
        elem = btn1.element;
    equal(elem.html(), 'ciao');
    btn1 = ui.button('<a>sdcbsjcbsjdbhcsd</a>', {text: 'foo'});
    elem = btn1.element;
    equal(elem.html(), 'foo');
});

test('icon', function () {
    expect(2);
    var ui = $.djpcms.ui,
        btn1 = ui.button({icon: 'icon-github'}),
        elem = btn1.element;
    equal(elem.html(), '<i class="icon-github"></i>');
    btn1 = ui.button('<a>foo</a>', {icon: 'icon-globe'})
    elem = btn1.element;
    equal(elem.html(), '<i class="icon-globe"></i>foo');
});