(function($){
    //
    $.popupWindow = (function () {
        var defaultSettings = {
            centerBrowser:0, // center window over browser window? {1 (YES) or 0 (NO)}. overrides top and left
            centerScreen:0, // center window over entire screen? {1 (YES) or 0 (NO)}. overrides top and left
            height: 500, // sets the height in pixels of the window.
            left: 0, // left position when the window appears.
            location: 0, // determines whether the address bar is displayed {1 (YES) or 0 (NO)}.
            menubar: 0, // determines whether the menu bar is displayed {1 (YES) or 0 (NO)}.
            resizable: 0, // whether the window can be resized {1 (YES) or 0 (NO)}. Can also be overloaded using resizable.
            scrollbars: 0, // determines whether scrollbars appear on the window {1 (YES) or 0 (NO)}.
            status: 0, // whether a status line appears at the bottom of the window {1 (YES) or 0 (NO)}.
            width: 500, // sets the width in pixels of the window.
            windowName: null, // name of window set from the name attribute of the element that invokes the click
            windowURL: null, // url used for the popup
            top: 0, // top position when the window appears.
            toolbar: 0 // determines whether a toolbar (includes the forward and back buttons) is displayed {1 (YES) or 0 (NO)}.
        },
    
        return function (instanceSettings) {
            var settings = $.extend({}, defaultSettings, instanceSettings || {}),
                centeredY,
                centeredX,
                windowFeatures = 'height=' + settings.height +
                                 ',width=' + settings.width +
                                 ',toolbar=' + settings.toolbar +
                                 ',scrollbars=' + settings.scrollbars +
                                 ',status=' + settings.status + 
                                 ',resizable=' + settings.resizable +
                                 ',location=' + settings.location +
                                 ',menuBar=' + settings.menubar;
            //
            settings.windowName = this.name || settings.windowName;
            if(settings.centerBrowser){
                if ($.browser.msie) {//hacked together for IE browsers
                    centeredY = (window.screenTop - 120) + ((((document.documentElement.clientHeight + 120)/2) - (settings.height/2)));
                    centeredX = window.screenLeft + ((((document.body.offsetWidth + 20)/2) - (settings.width/2)));
                } else {
                    centeredY = window.screenY + (((window.outerHeight/2) - (settings.height/2)));
                    centeredX = window.screenX + (((window.outerWidth/2) - (settings.width/2)));
                }
                window.open(settings.windowURL, settings.windowName, windowFeatures+',left=' + centeredX +',top=' + centeredY).focus();
            } else if(settings.centerScreen){
                centeredY = (screen.height - settings.height)/2;
                centeredX = (screen.width - settings.width)/2;
                window.open(settings.windowURL, settings.windowName, windowFeatures+',left=' + centeredX +',top=' + centeredY).focus();
            } else {
                window.open(settings.windowURL, settings.windowName, windowFeatures+',left=' + settings.left +',top=' + settings.top).focus();  
            }
        };
    }());
    /**
     * Popup decorator
     */
    if ($.djpcms) {
        $.djpcms.addJsonCallBack({
            name: "popup",
            handle: function (data, elem) {
                $.popupWindow({windowURL: data, centerBrowser: 1});
            }
        });
    }
}(jQuery));
