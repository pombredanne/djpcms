/*jslint evil: true, nomen: true, plusplus: true, browser: true */
/*globals jQuery*/
(function ($) {
    "use strict";
    $.djpcms.decorator({
        name: "chat-example",
        selector: '.chatroom',
        config: {
            path: '/ws/chat'
        },
        _create: function () {
            var self = this,
                url = 'ws://' + window.location.host + self.config.path,
                ws = new WebSocket(url);
            ws.onmessage = function(e) {
                var data = $.parseJSON(e.data);
                html = data.user + ': ' + data.message
                self.element.append(html)
                ws.send('');
            };
            ws.onopen = function() {
                ws.send('hi');
            };
        }
    });
}(jQuery));