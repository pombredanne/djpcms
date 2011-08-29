
(function($) {
    $.djpcms.decorator({
        id:"color_picker",
        decorate: function($this, config) {
            if(!$.fn.ColorPickerSetColor) {
                return;
            }
            $('input.color-picker', $this).each(function() {
                var iel = $(this).hide(),
                    div = iel.parent().addClass('color-picker'),
                    v = iel.val();
                //var div = $('<div class="color-picker"></div>');
                //var iel = $(this).hide().after(div);
                //var v = iel.val();
                //div.append(iel.remove());
                div.css('backgroundColor', '#' + v);
                div.ColorPicker({
                    onSubmit: function(hsb, hex, rgb, el) {
                        var elem = $(el);
                        $('input',elem).val(hex);
                        elem.css('backgroundColor', '#' + hex);
                        elem.ColorPickerHide();
                    },
                    onBeforeShow: function () {
                        var v = $('input',this).val();
                        $(this).ColorPickerSetColor(v);
                    }
                });
            });
        }
    });
}(jQuery));