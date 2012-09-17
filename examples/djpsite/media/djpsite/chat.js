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
            	var data, html, msg, i;
            	if(e.data) {
            		data = $.parseJSON(e.data)['chat'];
            		for(i=data.length-1; i>=0; i--) {
            			msg = data[i];
            			html = "<p><span class='user'>" + msg.user + '</span> : ' + msg.message + "</p>";
                		self.element.prepend(html);
            		}
            	}
            	ws.send('');
            };
            ws.onopen = function() {
                ws.send('hi');
            };
        }
    });
}(jQuery));