/*
 * Djpcms decorator for deleting a row from a table
 *
 */
/*jslint evil: true, nomen: true, plusplus: true, browser: true */
/*globals jQuery*/
(function ($) {
    "use strict";
    if ($.djpcms.ui.deleteTableRow === undefined) {
        $.djpcms.decorator({
            name: 'deleteTableRow',
            selector: 'table td.delete-row',
            config: {
                icon: 'icon-remove',
                classes: {
                    number_of_forms: 'number-of-forms'
                }
            },
            _create: function () {
                var self = this,
                    elem = self.element,
                    anchor;
                self.row = elem.parent('tr');
                if (self.row.length) {
                    anchor = $("<a href='#'></a>").appendTo(elem.html(''));
                    $.djpcms.ui.icon(anchor, self.config);
                    anchor.click(function (event) {
                        event.preventDefault();
                        self.handle_form();
                        self.row.remove();
                    });
                }
            },
            handle_form: function () {
                var enof = $(this.row.parents('form').first()).find('input.'+this.config.classes.number_of_forms),
                    nof;
                if (enof.length === 1) {
                    try {
                        nof = parseInt(enof.val(), 10) - 1;
                        enov.val(String(nof));
                    } catch (err) {}
                }
            }
        });
    }
}(jQuery));