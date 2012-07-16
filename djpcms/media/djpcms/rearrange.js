/*globals window, document, jQuery, console*/
/*jslint nomen: true, plusplus: true */
//
(function ($) {
    "use strict";
    /**
     * Page blocks rearranging
     */
    $.djpcms.decorator({
        name: "rearrange",
        selector: '.editable',
        config: {
            classes: {
                cmsblock: 'cms-edit-block',
                placeholder: 'cms-block-placeholder',
                cmsform: 'form.cms-blockcontent',
                movable: 'movable',
                sortblock: 'sortable-block'
            }
        },
        description: "Drag and drop functionalities in editing mode",
        _create: function () {
            var self = this,
                classes = self.config.classes,
                movable = '.' + classes.movable,
                cmsblock = '.' + classes.cmsblock,
                sortblock = '.' + classes.sortblock,
                columns = $(sortblock),
                holderelem = columns.commonAncestor(),
                curposition = null;
            //
            function position(elem) {
                var neighbour = elem.prev(cmsblock),
                    data = {};
                if (neighbour.length) {
                    data.previous = neighbour.attr('id');
                } else {
                    neighbour = elem.next(cmsblock);
                    if (neighbour.length) {
                        data.next = neighbour.attr('id');
                    }
                }
                return data;
            }
            //
            function moveblock(elem, pos, callback) {
                var form = $(classes.cmsform, elem),
                    data,
                    url;
                if (form.length) {
                    data = $.extend($.djpcms.ajaxparams('rearrange'), pos);
                    url = form.attr('action');
                    self.info('Updating position at "' + url + '"');
                    $.post(url, data, callback, 'json');
                }
            }
            //
            columns.delegate(cmsblock + movable + ' .hd', 'mousedown', function (event) {
                var block = $(this).parent(movable);
                if (block.length) {
                    curposition = position(block);
                }
            }).sortable({
                items: cmsblock,
                cancel: cmsblock + ":not(" + movable + ")",
                handle: '.hd',
                forcePlaceholderSize: true,
                connectWith: sortblock,
                revert: 300,
                delay: 100,
                opacity: 0.8,
                //containment: holderelem,
                placeholder: classes.placeholder,
                start: function (e, ui) {
                    var block = ui.item.addClass('dragging');
                    self.info('Moving ' + block.attr('id'));
                    block.width(block.width());
                },
                stop: function (e, ui) {
                    var elem = ui.item,
                        pos = position(elem);
                    self.info('Stopping ' + elem.attr('id'));
                    elem.css('width', '').removeClass('dragging');
                    if (pos.previous) {
                        if (pos.previous === curposition.previous) {return; }
                    } else {
                        if (pos.next === curposition.next) {return; }
                    }
                    columns.sortable('disable');
                    moveblock(elem, pos, function (e, s) {
                        columns.sortable('enable');
                        $.djpcms.jsonCallBack(e, s);
                    });
                }
            });
        }
    });
}(jQuery));