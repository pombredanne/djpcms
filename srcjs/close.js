// extend plugin scope
$.fn.extend({
    djpcms: function () {
        return $.djpcms.construct(this);
    }
});
}(jQuery));