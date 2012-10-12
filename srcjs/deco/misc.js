/**
 * Autocomplete Off
 */
$.djpcms.decorator({
    name: "autocomplete_off",
    decorate: function ($this) {
        $('.autocomplete-off', $this).each(function () {
            $(this).attr('autocomplete', 'off');
        });
        $('input:password', $this).each(function () {
            $(this).attr('autocomplete', 'off');
        });
    }
});
//
// Calendar Date Picker Decorator
$.djpcms.decorator({
    name: "datepicker",
    selector: 'input.dateinput',
    config: {
        dateFormat: 'd M yy'
    },
    _create: function () {
        this.element.datepicker(this.config);
    }
});
// Currency Input
$.djpcms.decorator({
    name: "numeric",
    selector: 'input.numeric',
    config: {
        classes: {
            negative: 'negative'
        }
    },
    format: function () {
        var elem = this.element,
            nc = this.config.classes.negative,
            v = $.djpcms.format_currency(elem.val());
        if (v.negative) {
            elem.addClass(nc);
        } else {
            elem.removeClass(nc);
        }
        elem.val(v.value);
    },
    _create: function () {
        var self = this;
        this.element.keyup(function () {
            self.format();
        });
    }
});