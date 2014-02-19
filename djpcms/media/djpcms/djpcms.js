/*!
 * jQuery Form Plugin
 * version: 3.09 (16-APR-2012)
 * @requires jQuery v1.3.2 or later
 *
 * Examples and documentation at: http://malsup.com/jquery/form/
 * Project repository: https://github.com/malsup/form
 * Dual licensed under the MIT and GPL licenses:
 *    http://malsup.github.com/mit-license.txt
 *    http://malsup.github.com/gpl-license-v2.txt
 */
/*global ActiveXObject alert */
;(function($) {
"use strict";

/*
    Usage Note:
    -----------
    Do not use both ajaxSubmit and ajaxForm on the same form.  These
    functions are mutually exclusive.  Use ajaxSubmit if you want
    to bind your own submit handler to the form.  For example,

    $(document).ready(function() {
        $('#myForm').on('submit', function(e) {
            e.preventDefault(); // <-- important
            $(this).ajaxSubmit({
                target: '#output'
            });
        });
    });

    Use ajaxForm when you want the plugin to manage all the event binding
    for you.  For example,

    $(document).ready(function() {
        $('#myForm').ajaxForm({
            target: '#output'
        });
    });
    
    You can also use ajaxForm with delegation (requires jQuery v1.7+), so the
    form does not have to exist when you invoke ajaxForm:

    $('#myForm').ajaxForm({
        delegation: true,
        target: '#output'
    });
    
    When using ajaxForm, the ajaxSubmit function will be invoked for you
    at the appropriate time.
*/

/**
 * Feature detection
 */
var feature = {};
feature.fileapi = $("<input type='file'/>").get(0).files !== undefined;
feature.formdata = window.FormData !== undefined;

/**
 * ajaxSubmit() provides a mechanism for immediately submitting
 * an HTML form using AJAX.
 */
$.fn.ajaxSubmit = function(options) {
    /*jshint scripturl:true */

    // fast fail if nothing selected (http://dev.jquery.com/ticket/2752)
    if (!this.length) {
        log('ajaxSubmit: skipping submit process - no element selected');
        return this;
    }
    
    var method, action, url, $form = this;

    if (typeof options == 'function') {
        options = { success: options };
    }

    method = this.attr('method');
    action = this.attr('action');
    url = (typeof action === 'string') ? $.trim(action) : '';
    url = url || window.location.href || '';
    if (url) {
        // clean url (don't include hash vaue)
        url = (url.match(/^([^#]+)/)||[])[1];
    }

    options = $.extend(true, {
        url:  url,
        success: $.ajaxSettings.success,
        type: method || 'GET',
        iframeSrc: /^https/i.test(window.location.href || '') ? 'javascript:false' : 'about:blank'
    }, options);

    // hook for manipulating the form data before it is extracted;
    // convenient for use with rich editors like tinyMCE or FCKEditor
    var veto = {};
    this.trigger('form-pre-serialize', [this, options, veto]);
    if (veto.veto) {
        log('ajaxSubmit: submit vetoed via form-pre-serialize trigger');
        return this;
    }

    // provide opportunity to alter form data before it is serialized
    if (options.beforeSerialize && options.beforeSerialize(this, options) === false) {
        log('ajaxSubmit: submit aborted via beforeSerialize callback');
        return this;
    }

    var traditional = options.traditional;
    if ( traditional === undefined ) {
        traditional = $.ajaxSettings.traditional;
    }
    
    var elements = [];
    var qx, a = this.formToArray(options.semantic, elements);
    if (options.data) {
        options.extraData = options.data;
        qx = $.param(options.data, traditional);
    }

    // give pre-submit callback an opportunity to abort the submit
    if (options.beforeSubmit && options.beforeSubmit(a, this, options) === false) {
        log('ajaxSubmit: submit aborted via beforeSubmit callback');
        return this;
    }

    // fire vetoable 'validate' event
    this.trigger('form-submit-validate', [a, this, options, veto]);
    if (veto.veto) {
        log('ajaxSubmit: submit vetoed via form-submit-validate trigger');
        return this;
    }

    var q = $.param(a, traditional);
    if (qx) {
        q = ( q ? (q + '&' + qx) : qx );
    }    
    if (options.type.toUpperCase() == 'GET') {
        options.url += (options.url.indexOf('?') >= 0 ? '&' : '?') + q;
        options.data = null;  // data is null for 'get'
    }
    else {
        options.data = q; // data is the query string for 'post'
    }

    var callbacks = [];
    if (options.resetForm) {
        callbacks.push(function() { $form.resetForm(); });
    }
    if (options.clearForm) {
        callbacks.push(function() { $form.clearForm(options.includeHidden); });
    }

    // perform a load on the target only if dataType is not provided
    if (!options.dataType && options.target) {
        var oldSuccess = options.success || function(){};
        callbacks.push(function(data) {
            var fn = options.replaceTarget ? 'replaceWith' : 'html';
            $(options.target)[fn](data).each(oldSuccess, arguments);
        });
    }
    else if (options.success) {
        callbacks.push(options.success);
    }

    options.success = function(data, status, xhr) { // jQuery 1.4+ passes xhr as 3rd arg
        var context = options.context || options;    // jQuery 1.4+ supports scope context 
        for (var i=0, max=callbacks.length; i < max; i++) {
            callbacks[i].apply(context, [data, status, xhr || $form, $form]);
        }
    };

    // are there files to upload?
    var fileInputs = $('input:file:enabled[value]', this); // [value] (issue #113)
    var hasFileInputs = fileInputs.length > 0;
    var mp = 'multipart/form-data';
    var multipart = ($form.attr('enctype') == mp || $form.attr('encoding') == mp);

    var fileAPI = feature.fileapi && feature.formdata;
    log("fileAPI :" + fileAPI);
    var shouldUseFrame = (hasFileInputs || multipart) && !fileAPI;

    // options.iframe allows user to force iframe mode
    // 06-NOV-09: now defaulting to iframe mode if file input is detected
    if (options.iframe !== false && (options.iframe || shouldUseFrame)) {
        // hack to fix Safari hang (thanks to Tim Molendijk for this)
        // see:  http://groups.google.com/group/jquery-dev/browse_thread/thread/36395b7ab510dd5d
        if (options.closeKeepAlive) {
            $.get(options.closeKeepAlive, function() {
                fileUploadIframe(a);
            });
        }
          else {
            fileUploadIframe(a);
          }
    }
    else if ((hasFileInputs || multipart) && fileAPI) {
        fileUploadXhr(a);
    }
    else {
        $.ajax(options);
    }

    // clear element array
    for (var k=0; k < elements.length; k++)
        elements[k] = null;

    // fire 'notify' event
    this.trigger('form-submit-notify', [this, options]);
    return this;

     // XMLHttpRequest Level 2 file uploads (big hat tip to francois2metz)
    function fileUploadXhr(a) {
        var formdata = new FormData();

        for (var i=0; i < a.length; i++) {
            formdata.append(a[i].name, a[i].value);
        }

        if (options.extraData) {
            for (var p in options.extraData)
                if (options.extraData.hasOwnProperty(p))
                    formdata.append(p, options.extraData[p]);
        }

        options.data = null;

        var s = $.extend(true, {}, $.ajaxSettings, options, {
            contentType: false,
            processData: false,
            cache: false,
            type: 'POST'
        });
        
        if (options.uploadProgress) {
            // workaround because jqXHR does not expose upload property
            s.xhr = function() {
                var xhr = jQuery.ajaxSettings.xhr();
                if (xhr.upload) {
                    xhr.upload.onprogress = function(event) {
                        var percent = 0;
                        var position = event.loaded || event.position; /*event.position is deprecated*/
                        var total = event.total;
                        if (event.lengthComputable) {
                            percent = Math.ceil(position / total * 100);
                        }
                        options.uploadProgress(event, position, total, percent);
                    };
                }
                return xhr;
            };
        }

        s.data = null;
          var beforeSend = s.beforeSend;
          s.beforeSend = function(xhr, o) {
              o.data = formdata;
            if(beforeSend)
                beforeSend.call(o, xhr, options);
        };
        $.ajax(s);
    }

    // private function for handling file uploads (hat tip to YAHOO!)
    function fileUploadIframe(a) {
        var form = $form[0], el, i, s, g, id, $io, io, xhr, sub, n, timedOut, timeoutHandle;
        var useProp = !!$.fn.prop;

        if ($(':input[name=submit],:input[id=submit]', form).length) {
            // if there is an input with a name or id of 'submit' then we won't be
            // able to invoke the submit fn on the form (at least not x-browser)
            alert('Error: Form elements must not have name or id of "submit".');
            return;
        }
        
        if (a) {
            // ensure that every serialized input is still enabled
            for (i=0; i < elements.length; i++) {
                el = $(elements[i]);
                if ( useProp )
                    el.prop('disabled', false);
                else
                    el.removeAttr('disabled');
            }
        }

        s = $.extend(true, {}, $.ajaxSettings, options);
        s.context = s.context || s;
        id = 'jqFormIO' + (new Date().getTime());
        if (s.iframeTarget) {
            $io = $(s.iframeTarget);
            n = $io.attr('name');
            if (!n)
                 $io.attr('name', id);
            else
                id = n;
        }
        else {
            $io = $('<iframe name="' + id + '" src="'+ s.iframeSrc +'" />');
            $io.css({ position: 'absolute', top: '-1000px', left: '-1000px' });
        }
        io = $io[0];


        xhr = { // mock object
            aborted: 0,
            responseText: null,
            responseXML: null,
            status: 0,
            statusText: 'n/a',
            getAllResponseHeaders: function() {},
            getResponseHeader: function() {},
            setRequestHeader: function() {},
            abort: function(status) {
                var e = (status === 'timeout' ? 'timeout' : 'aborted');
                log('aborting upload... ' + e);
                this.aborted = 1;
                $io.attr('src', s.iframeSrc); // abort op in progress
                xhr.error = e;
                if (s.error)
                    s.error.call(s.context, xhr, e, status);
                if (g)
                    $.event.trigger("ajaxError", [xhr, s, e]);
                if (s.complete)
                    s.complete.call(s.context, xhr, e);
            }
        };

        g = s.global;
        // trigger ajax global events so that activity/block indicators work like normal
        if (g && 0 === $.active++) {
            $.event.trigger("ajaxStart");
        }
        if (g) {
            $.event.trigger("ajaxSend", [xhr, s]);
        }

        if (s.beforeSend && s.beforeSend.call(s.context, xhr, s) === false) {
            if (s.global) {
                $.active--;
            }
            return;
        }
        if (xhr.aborted) {
            return;
        }

        // add submitting element to data if we know it
        sub = form.clk;
        if (sub) {
            n = sub.name;
            if (n && !sub.disabled) {
                s.extraData = s.extraData || {};
                s.extraData[n] = sub.value;
                if (sub.type == "image") {
                    s.extraData[n+'.x'] = form.clk_x;
                    s.extraData[n+'.y'] = form.clk_y;
                }
            }
        }
        
        var CLIENT_TIMEOUT_ABORT = 1;
        var SERVER_ABORT = 2;

        function getDoc(frame) {
            var doc = frame.contentWindow ? frame.contentWindow.document : frame.contentDocument ? frame.contentDocument : frame.document;
            return doc;
        }
        
        // Rails CSRF hack (thanks to Yvan Barthelemy)
        var csrf_token = $('meta[name=csrf-token]').attr('content');
        var csrf_param = $('meta[name=csrf-param]').attr('content');
        if (csrf_param && csrf_token) {
            s.extraData = s.extraData || {};
            s.extraData[csrf_param] = csrf_token;
        }

        // take a breath so that pending repaints get some cpu time before the upload starts
        function doSubmit() {
            // make sure form attrs are set
            var t = $form.attr('target'), a = $form.attr('action');

            // update form attrs in IE friendly way
            form.setAttribute('target',id);
            if (!method) {
                form.setAttribute('method', 'POST');
            }
            if (a != s.url) {
                form.setAttribute('action', s.url);
            }

            // ie borks in some cases when setting encoding
            if (! s.skipEncodingOverride && (!method || /post/i.test(method))) {
                $form.attr({
                    encoding: 'multipart/form-data',
                    enctype:  'multipart/form-data'
                });
            }

            // support timout
            if (s.timeout) {
                timeoutHandle = setTimeout(function() { timedOut = true; cb(CLIENT_TIMEOUT_ABORT); }, s.timeout);
            }
            
            // look for server aborts
            function checkState() {
                try {
                    var state = getDoc(io).readyState;
                    log('state = ' + state);
                    if (state && state.toLowerCase() == 'uninitialized')
                        setTimeout(checkState,50);
                }
                catch(e) {
                    log('Server abort: ' , e, ' (', e.name, ')');
                    cb(SERVER_ABORT);
                    if (timeoutHandle)
                        clearTimeout(timeoutHandle);
                    timeoutHandle = undefined;
                }
            }

            // add "extra" data to form if provided in options
            var extraInputs = [];
            try {
                if (s.extraData) {
                    for (var n in s.extraData) {
                        if (s.extraData.hasOwnProperty(n)) {
                            extraInputs.push(
                                $('<input type="hidden" name="'+n+'">').attr('value',s.extraData[n])
                                    .appendTo(form)[0]);
                        }
                    }
                }

                if (!s.iframeTarget) {
                    // add iframe to doc and submit the form
                    $io.appendTo('body');
                    if (io.attachEvent)
                        io.attachEvent('onload', cb);
                    else
                        io.addEventListener('load', cb, false);
                }
                setTimeout(checkState,15);
                form.submit();
            }
            finally {
                // reset attrs and remove "extra" input elements
                form.setAttribute('action',a);
                if(t) {
                    form.setAttribute('target', t);
                } else {
                    $form.removeAttr('target');
                }
                $(extraInputs).remove();
            }
        }

        if (s.forceSync) {
            doSubmit();
        }
        else {
            setTimeout(doSubmit, 10); // this lets dom updates render
        }

        var data, doc, domCheckCount = 50, callbackProcessed;

        function cb(e) {
            if (xhr.aborted || callbackProcessed) {
                return;
            }
            try {
                doc = getDoc(io);
            }
            catch(ex) {
                log('cannot access response document: ', ex);
                e = SERVER_ABORT;
            }
            if (e === CLIENT_TIMEOUT_ABORT && xhr) {
                xhr.abort('timeout');
                return;
            }
            else if (e == SERVER_ABORT && xhr) {
                xhr.abort('server abort');
                return;
            }

            if (!doc || doc.location.href == s.iframeSrc) {
                // response not received yet
                if (!timedOut)
                    return;
            }
            if (io.detachEvent)
                io.detachEvent('onload', cb);
            else    
                io.removeEventListener('load', cb, false);

            var status = 'success', errMsg;
            try {
                if (timedOut) {
                    throw 'timeout';
                }

                var isXml = s.dataType == 'xml' || doc.XMLDocument || $.isXMLDoc(doc);
                log('isXml='+isXml);
                if (!isXml && window.opera && (doc.body === null || !doc.body.innerHTML)) {
                    if (--domCheckCount) {
                        // in some browsers (Opera) the iframe DOM is not always traversable when
                        // the onload callback fires, so we loop a bit to accommodate
                        log('requeing onLoad callback, DOM not available');
                        setTimeout(cb, 250);
                        return;
                    }
                    // let this fall through because server response could be an empty document
                    //log('Could not access iframe DOM after mutiple tries.');
                    //throw 'DOMException: not available';
                }

                //log('response detected');
                var docRoot = doc.body ? doc.body : doc.documentElement;
                xhr.responseText = docRoot ? docRoot.innerHTML : null;
                xhr.responseXML = doc.XMLDocument ? doc.XMLDocument : doc;
                if (isXml)
                    s.dataType = 'xml';
                xhr.getResponseHeader = function(header){
                    var headers = {'content-type': s.dataType};
                    return headers[header];
                };
                // support for XHR 'status' & 'statusText' emulation :
                if (docRoot) {
                    xhr.status = Number( docRoot.getAttribute('status') ) || xhr.status;
                    xhr.statusText = docRoot.getAttribute('statusText') || xhr.statusText;
                }

                var dt = (s.dataType || '').toLowerCase();
                var scr = /(json|script|text)/.test(dt);
                if (scr || s.textarea) {
                    // see if user embedded response in textarea
                    var ta = doc.getElementsByTagName('textarea')[0];
                    if (ta) {
                        xhr.responseText = ta.value;
                        // support for XHR 'status' & 'statusText' emulation :
                        xhr.status = Number( ta.getAttribute('status') ) || xhr.status;
                        xhr.statusText = ta.getAttribute('statusText') || xhr.statusText;
                    }
                    else if (scr) {
                        // account for browsers injecting pre around json response
                        var pre = doc.getElementsByTagName('pre')[0];
                        var b = doc.getElementsByTagName('body')[0];
                        if (pre) {
                            xhr.responseText = pre.textContent ? pre.textContent : pre.innerText;
                        }
                        else if (b) {
                            xhr.responseText = b.textContent ? b.textContent : b.innerText;
                        }
                    }
                }
                else if (dt == 'xml' && !xhr.responseXML && xhr.responseText) {
                    xhr.responseXML = toXml(xhr.responseText);
                }

                try {
                    data = httpData(xhr, dt, s);
                }
                catch (e) {
                    status = 'parsererror';
                    xhr.error = errMsg = (e || status);
                }
            }
            catch (e) {
                log('error caught: ',e);
                status = 'error';
                xhr.error = errMsg = (e || status);
            }

            if (xhr.aborted) {
                log('upload aborted');
                status = null;
            }

            if (xhr.status) { // we've set xhr.status
                status = (xhr.status >= 200 && xhr.status < 300 || xhr.status === 304) ? 'success' : 'error';
            }

            // ordering of these callbacks/triggers is odd, but that's how $.ajax does it
            if (status === 'success') {
                if (s.success)
                    s.success.call(s.context, data, 'success', xhr);
                if (g)
                    $.event.trigger("ajaxSuccess", [xhr, s]);
            }
            else if (status) {
                if (errMsg === undefined)
                    errMsg = xhr.statusText;
                if (s.error)
                    s.error.call(s.context, xhr, status, errMsg);
                if (g)
                    $.event.trigger("ajaxError", [xhr, s, errMsg]);
            }

            if (g)
                $.event.trigger("ajaxComplete", [xhr, s]);

            if (g && ! --$.active) {
                $.event.trigger("ajaxStop");
            }

            if (s.complete)
                s.complete.call(s.context, xhr, status);

            callbackProcessed = true;
            if (s.timeout)
                clearTimeout(timeoutHandle);

            // clean up
            setTimeout(function() {
                if (!s.iframeTarget)
                    $io.remove();
                xhr.responseXML = null;
            }, 100);
        }

        var toXml = $.parseXML || function(s, doc) { // use parseXML if available (jQuery 1.5+)
            if (window.ActiveXObject) {
                doc = new ActiveXObject('Microsoft.XMLDOM');
                doc.async = 'false';
                doc.loadXML(s);
            }
            else {
                doc = (new DOMParser()).parseFromString(s, 'text/xml');
            }
            return (doc && doc.documentElement && doc.documentElement.nodeName != 'parsererror') ? doc : null;
        };
        var parseJSON = $.parseJSON || function(s) {
            /*jslint evil:true */
            return window['eval']('(' + s + ')');
        };

        var httpData = function( xhr, type, s ) { // mostly lifted from jq1.4.4

            var ct = xhr.getResponseHeader('content-type') || '',
                xml = type === 'xml' || !type && ct.indexOf('xml') >= 0,
                data = xml ? xhr.responseXML : xhr.responseText;

            if (xml && data.documentElement.nodeName === 'parsererror') {
                if ($.error)
                    $.error('parsererror');
            }
            if (s && s.dataFilter) {
                data = s.dataFilter(data, type);
            }
            if (typeof data === 'string') {
                if (type === 'json' || !type && ct.indexOf('json') >= 0) {
                    data = parseJSON(data);
                } else if (type === "script" || !type && ct.indexOf("javascript") >= 0) {
                    $.globalEval(data);
                }
            }
            return data;
        };
    }
};

/**
 * ajaxForm() provides a mechanism for fully automating form submission.
 *
 * The advantages of using this method instead of ajaxSubmit() are:
 *
 * 1: This method will include coordinates for <input type="image" /> elements (if the element
 *    is used to submit the form).
 * 2. This method will include the submit element's name/value data (for the element that was
 *    used to submit the form).
 * 3. This method binds the submit() method to the form for you.
 *
 * The options argument for ajaxForm works exactly as it does for ajaxSubmit.  ajaxForm merely
 * passes the options argument along after properly binding events for submit elements and
 * the form itself.
 */
$.fn.ajaxForm = function(options) {
    options = options || {};
    options.delegation = options.delegation && $.isFunction($.fn.on);
    
    // in jQuery 1.3+ we can fix mistakes with the ready state
    if (!options.delegation && this.length === 0) {
        var o = { s: this.selector, c: this.context };
        if (!$.isReady && o.s) {
            log('DOM not ready, queuing ajaxForm');
            $(function() {
                $(o.s,o.c).ajaxForm(options);
            });
            return this;
        }
        // is your DOM ready?  http://docs.jquery.com/Tutorials:Introducing_$(document).ready()
        log('terminating; zero elements found by selector' + ($.isReady ? '' : ' (DOM not ready)'));
        return this;
    }

    if ( options.delegation ) {
        $(document)
            .off('submit.form-plugin', this.selector, doAjaxSubmit)
            .off('click.form-plugin', this.selector, captureSubmittingElement)
            .on('submit.form-plugin', this.selector, options, doAjaxSubmit)
            .on('click.form-plugin', this.selector, options, captureSubmittingElement);
        return this;
    }

    return this.ajaxFormUnbind()
        .bind('submit.form-plugin', options, doAjaxSubmit)
        .bind('click.form-plugin', options, captureSubmittingElement);
};

// private event handlers    
function doAjaxSubmit(e) {
    /*jshint validthis:true */
    var options = e.data;
    if (!e.isDefaultPrevented()) { // if event has been canceled, don't proceed
        e.preventDefault();
        $(this).ajaxSubmit(options);
    }
}
    
function captureSubmittingElement(e) {
    /*jshint validthis:true */
    var target = e.target;
    var $el = $(target);
    if (!($el.is(":submit,input:image"))) {
        // is this a child element of the submit el?  (ex: a span within a button)
        var t = $el.closest(':submit');
        if (t.length === 0) {
            return;
        }
        target = t[0];
    }
    var form = this;
    form.clk = target;
    if (target.type == 'image') {
        if (e.offsetX !== undefined) {
            form.clk_x = e.offsetX;
            form.clk_y = e.offsetY;
        } else if (typeof $.fn.offset == 'function') {
            var offset = $el.offset();
            form.clk_x = e.pageX - offset.left;
            form.clk_y = e.pageY - offset.top;
        } else {
            form.clk_x = e.pageX - target.offsetLeft;
            form.clk_y = e.pageY - target.offsetTop;
        }
    }
    // clear form vars
    setTimeout(function() { form.clk = form.clk_x = form.clk_y = null; }, 100);
}


// ajaxFormUnbind unbinds the event handlers that were bound by ajaxForm
$.fn.ajaxFormUnbind = function() {
    return this.unbind('submit.form-plugin click.form-plugin');
};

/**
 * formToArray() gathers form element data into an array of objects that can
 * be passed to any of the following ajax functions: $.get, $.post, or load.
 * Each object in the array has both a 'name' and 'value' property.  An example of
 * an array for a simple login form might be:
 *
 * [ { name: 'username', value: 'jresig' }, { name: 'password', value: 'secret' } ]
 *
 * It is this array that is passed to pre-submit callback functions provided to the
 * ajaxSubmit() and ajaxForm() methods.
 */
$.fn.formToArray = function(semantic, elements) {
    var a = [];
    if (this.length === 0) {
        return a;
    }

    var form = this[0];
    var els = semantic ? form.getElementsByTagName('*') : form.elements;
    if (!els) {
        return a;
    }

    var i,j,n,v,el,max,jmax;
    for(i=0, max=els.length; i < max; i++) {
        el = els[i];
        n = el.name;
        if (!n) {
            continue;
        }

        if (semantic && form.clk && el.type == "image") {
            // handle image inputs on the fly when semantic == true
            if(!el.disabled && form.clk == el) {
                a.push({name: n, value: $(el).val(), type: el.type });
                a.push({name: n+'.x', value: form.clk_x}, {name: n+'.y', value: form.clk_y});
            }
            continue;
        }

        v = $.fieldValue(el, true);
        if (v && v.constructor == Array) {
            if (elements) 
                elements.push(el);
            for(j=0, jmax=v.length; j < jmax; j++) {
                a.push({name: n, value: v[j]});
            }
        }
        else if (feature.fileapi && el.type == 'file' && !el.disabled) {
            if (elements) 
                elements.push(el);
            var files = el.files;
            if (files.length) {
                for (j=0; j < files.length; j++) {
                    a.push({name: n, value: files[j], type: el.type});
                }
            }
            else {
                // #180
                a.push({ name: n, value: '', type: el.type });
            }
        }
        else if (v !== null && typeof v != 'undefined') {
            if (elements) 
                elements.push(el);
            a.push({name: n, value: v, type: el.type, required: el.required});
        }
    }

    if (!semantic && form.clk) {
        // input type=='image' are not found in elements array! handle it here
        var $input = $(form.clk), input = $input[0];
        n = input.name;
        if (n && !input.disabled && input.type == 'image') {
            a.push({name: n, value: $input.val()});
            a.push({name: n+'.x', value: form.clk_x}, {name: n+'.y', value: form.clk_y});
        }
    }
    return a;
};

/**
 * Serializes form data into a 'submittable' string. This method will return a string
 * in the format: name1=value1&amp;name2=value2
 */
$.fn.formSerialize = function(semantic) {
    //hand off to jQuery.param for proper encoding
    return $.param(this.formToArray(semantic));
};

/**
 * Serializes all field elements in the jQuery object into a query string.
 * This method will return a string in the format: name1=value1&amp;name2=value2
 */
$.fn.fieldSerialize = function(successful) {
    var a = [];
    this.each(function() {
        var n = this.name;
        if (!n) {
            return;
        }
        var v = $.fieldValue(this, successful);
        if (v && v.constructor == Array) {
            for (var i=0,max=v.length; i < max; i++) {
                a.push({name: n, value: v[i]});
            }
        }
        else if (v !== null && typeof v != 'undefined') {
            a.push({name: this.name, value: v});
        }
    });
    //hand off to jQuery.param for proper encoding
    return $.param(a);
};

/**
 * Returns the value(s) of the element in the matched set.  For example, consider the following form:
 *
 *  <form><fieldset>
 *      <input name="A" type="text" />
 *      <input name="A" type="text" />
 *      <input name="B" type="checkbox" value="B1" />
 *      <input name="B" type="checkbox" value="B2"/>
 *      <input name="C" type="radio" value="C1" />
 *      <input name="C" type="radio" value="C2" />
 *  </fieldset></form>
 *
 *  var v = $(':text').fieldValue();
 *  // if no values are entered into the text inputs
 *  v == ['','']
 *  // if values entered into the text inputs are 'foo' and 'bar'
 *  v == ['foo','bar']
 *
 *  var v = $(':checkbox').fieldValue();
 *  // if neither checkbox is checked
 *  v === undefined
 *  // if both checkboxes are checked
 *  v == ['B1', 'B2']
 *
 *  var v = $(':radio').fieldValue();
 *  // if neither radio is checked
 *  v === undefined
 *  // if first radio is checked
 *  v == ['C1']
 *
 * The successful argument controls whether or not the field element must be 'successful'
 * (per http://www.w3.org/TR/html4/interact/forms.html#successful-controls).
 * The default value of the successful argument is true.  If this value is false the value(s)
 * for each element is returned.
 *
 * Note: This method *always* returns an array.  If no valid value can be determined the
 *    array will be empty, otherwise it will contain one or more values.
 */
$.fn.fieldValue = function(successful) {
    for (var val=[], i=0, max=this.length; i < max; i++) {
        var el = this[i];
        var v = $.fieldValue(el, successful);
        if (v === null || typeof v == 'undefined' || (v.constructor == Array && !v.length)) {
            continue;
        }
        if (v.constructor == Array)
            $.merge(val, v);
        else
            val.push(v);
    }
    return val;
};

/**
 * Returns the value of the field element.
 */
$.fieldValue = function(el, successful) {
    var n = el.name, t = el.type, tag = el.tagName.toLowerCase();
    if (successful === undefined) {
        successful = true;
    }

    if (successful && (!n || el.disabled || t == 'reset' || t == 'button' ||
        (t == 'checkbox' || t == 'radio') && !el.checked ||
        (t == 'submit' || t == 'image') && el.form && el.form.clk != el ||
        tag == 'select' && el.selectedIndex == -1)) {
            return null;
    }

    if (tag == 'select') {
        var index = el.selectedIndex;
        if (index < 0) {
            return null;
        }
        var a = [], ops = el.options;
        var one = (t == 'select-one');
        var max = (one ? index+1 : ops.length);
        for(var i=(one ? index : 0); i < max; i++) {
            var op = ops[i];
            if (op.selected) {
                var v = op.value;
                if (!v) { // extra pain for IE...
                    v = (op.attributes && op.attributes.value && !(op.attributes.value.specified)) ? op.text : op.value;
                }
                if (one) {
                    return v;
                }
                a.push(v);
            }
        }
        return a;
    }
    return $(el).val();
};

/**
 * Clears the form data.  Takes the following actions on the form's input fields:
 *  - input text fields will have their 'value' property set to the empty string
 *  - select elements will have their 'selectedIndex' property set to -1
 *  - checkbox and radio inputs will have their 'checked' property set to false
 *  - inputs of type submit, button, reset, and hidden will *not* be effected
 *  - button elements will *not* be effected
 */
$.fn.clearForm = function(includeHidden) {
    return this.each(function() {
        $('input,select,textarea', this).clearFields(includeHidden);
    });
};

/**
 * Clears the selected form elements.
 */
$.fn.clearFields = $.fn.clearInputs = function(includeHidden) {
    var re = /^(?:color|date|datetime|email|month|number|password|range|search|tel|text|time|url|week)$/i; // 'hidden' is not in this list
    return this.each(function() {
        var t = this.type, tag = this.tagName.toLowerCase();
        if (re.test(t) || tag == 'textarea') {
            this.value = '';
        }
        else if (t == 'checkbox' || t == 'radio') {
            this.checked = false;
        }
        else if (tag == 'select') {
            this.selectedIndex = -1;
        }
        else if (includeHidden) {
            // includeHidden can be the valud true, or it can be a selector string
            // indicating a special test; for example:
            //  $('#myForm').clearForm('.special:hidden')
            // the above would clean hidden inputs that have the class of 'special'
            if ( (includeHidden === true && /hidden/.test(t)) ||
                 (typeof includeHidden == 'string' && $(this).is(includeHidden)) )
                this.value = '';
        }
    });
};

/**
 * Resets the form data.  Causes all form elements to be reset to their original value.
 */
$.fn.resetForm = function() {
    return this.each(function() {
        // guard against an input with the name of 'reset'
        // note that IE reports the reset function as an 'object'
        if (typeof this.reset == 'function' || (typeof this.reset == 'object' && !this.reset.nodeType)) {
            this.reset();
        }
    });
};

/**
 * Enables or disables any matching elements.
 */
$.fn.enable = function(b) {
    if (b === undefined) {
        b = true;
    }
    return this.each(function() {
        this.disabled = !b;
    });
};

/**
 * Checks/unchecks any matching checkboxes or radio buttons and
 * selects/deselects and matching option elements.
 */
$.fn.selected = function(select) {
    if (select === undefined) {
        select = true;
    }
    return this.each(function() {
        var t = this.type;
        if (t == 'checkbox' || t == 'radio') {
            this.checked = select;
        }
        else if (this.tagName.toLowerCase() == 'option') {
            var $sel = $(this).parent('select');
            if (select && $sel[0] && $sel[0].type == 'select-one') {
                // deselect all other options
                $sel.find('option').selected(false);
            }
            this.selected = select;
        }
    });
};

// expose debug var
$.fn.ajaxSubmit.debug = false;

// helper fn for console logging
function log() {
    if (!$.fn.ajaxSubmit.debug) 
        return;
    var msg = '[jquery.form] ' + Array.prototype.join.call(arguments,'');
    if (window.console && window.console.log) {
        window.console.log(msg);
    }
    else if (window.opera && window.opera.postError) {
        window.opera.postError(msg);
    }
}

})(jQuery);

/*jslint browser: true */ /*global jQuery: true */

/**
 * jQuery Cookie plugin
 *
 * Copyright (c) 2010 Klaus Hartl (stilbuero.de)
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 */

// TODO JsDoc

/**
 * Create a cookie with the given key and value and other optional parameters.
 *
 * @example $.cookie('the_cookie', 'the_value');
 * @desc Set the value of a cookie.
 * @example $.cookie('the_cookie', 'the_value', { expires: 7, path: '/', domain: 'jquery.com', secure: true });
 * @desc Create a cookie with all available options.
 * @example $.cookie('the_cookie', 'the_value');
 * @desc Create a session cookie.
 * @example $.cookie('the_cookie', null);
 * @desc Delete a cookie by passing null as value. Keep in mind that you have to use the same path and domain
 *       used when the cookie was set.
 *
 * @param String key The key of the cookie.
 * @param String value The value of the cookie.
 * @param Object options An object literal containing key/value pairs to provide optional cookie attributes.
 * @option Number|Date expires Either an integer specifying the expiration date from now on in days or a Date object.
 *                             If a negative value is specified (e.g. a date in the past), the cookie will be deleted.
 *                             If set to null or omitted, the cookie will be a session cookie and will not be retained
 *                             when the the browser exits.
 * @option String path The value of the path atribute of the cookie (default: path of page that created the cookie).
 * @option String domain The value of the domain attribute of the cookie (default: domain of page that created the cookie).
 * @option Boolean secure If true, the secure attribute of the cookie will be set and the cookie transmission will
 *                        require a secure protocol (like HTTPS).
 * @type undefined
 *
 * @name $.cookie
 * @cat Plugins/Cookie
 * @author Klaus Hartl/klaus.hartl@stilbuero.de
 */

/**
 * Get the value of a cookie with the given key.
 *
 * @example $.cookie('the_cookie');
 * @desc Get the value of a cookie.
 *
 * @param String key The key of the cookie.
 * @return The value of the cookie.
 * @type String
 *
 * @name $.cookie
 * @cat Plugins/Cookie
 * @author Klaus Hartl/klaus.hartl@stilbuero.de
 */
jQuery.cookie = function (key, value, options) {

    // key and value given, set cookie...
    if (arguments.length > 1 && (value === null || typeof value !== "object")) {
        options = jQuery.extend({}, options);

        if (value === null) {
            options.expires = -1;
        }

        if (typeof options.expires === 'number') {
            var days = options.expires, t = options.expires = new Date();
            t.setDate(t.getDate() + days);
        }

        return (document.cookie = [
            encodeURIComponent(key), '=',
            options.raw ? String(value) : encodeURIComponent(String(value)),
            options.expires ? '; expires=' + options.expires.toUTCString() : '', // use expires attribute, max-age is not supported by IE
            options.path ? '; path=' + options.path : '',
            options.domain ? '; domain=' + options.domain : '',
            options.secure ? '; secure' : ''
        ].join(''));
    }

    // key and possibly options given, get cookie...
    options = value || {};
    var result, decode = options.raw ? function (s) { return s; } : decodeURIComponent;
    return (result = new RegExp('(?:^|; )' + encodeURIComponent(key) + '=([^;]*)').exec(document.cookie)) ? decode(result[1]) : null;
};

exports = {};
(function ($) {
"use strict";
/**
 * Logging module for djpcms. Usage
 *
 * var logger = $.logging.getLogger();
 * logger.info('bla')
 */
$.logging = (function () {
    var levelNames = {},
        logging = {
            loggers: {},
            mapping: {},
            names: {},
            format_error: function (msg, e) {
                if (e !== undefined) {
                    msg += "- File " + e.fileName + " - Line " + e.lineNumber + ": " + e;
                }
                return msg;
            },
            debug: 10,
            info: 20,
            warn: 30,
            error: 40,
            critical: 50,
            logclass: 'log'
        };
    // Logging levels
    logging.levels = {
        debug: {
            level: logging.debug,
            name: 'DEBUG'
        },
        info: {
            level: logging.info,
            name: 'INFO'
        },
        warn: {
            level: logging.warn,
            name: 'WARN'
        },
        error: {
            level: logging.error,
            name: 'ERROR',
            f: function (msg, e) {
                return logging.format_error(msg, e);
            }
        },
        critical: {
            level: logging.critical,
            name: 'CRITICAL',
            f: function (msg, e) {
                return logging.format_error(msg, e);
            }
        }
    };
    // Create the mapping between level number and level name
    $.each(logging.levels, function (name, level) {
        levelNames[level.level] = level;
    });
    logging.getLevelName = function (level) {
        var l = levelNames[level];
        if (l !== undefined) {
            l = l.name;
        } else {
            l = 'Level-' + level;
        }
        return l;
    };
    // Default formatter
    logging.default_formatter = function (msg, lvl) {
        var mlevel = logging.getLevelName(lvl),
            dte = new Date(),
            hours = dte.getHours(),
            minutes = dte.getMinutes(),
            seconds = dte.getSeconds();
        if (hours < 10) {hours = '0' + hours; }
        if (minutes < 10) {minutes = '0' + minutes; }
        if (seconds < 10) {seconds = '0' + seconds; }
        return hours + ':' + minutes + ':' + seconds + ' - ' + mlevel + ' - ' + msg;
    };
    // HTML formatter
    logging.html_formatter = function (msg, lvl) {
        var mlevel = logging.getLevelName(lvl);
        msg = logging.default_formatter(msg, lvl);
        return '<pre class="' + logging.logclass + ' ' + mlevel.toLowerCase() + '">' + msg + '</pre>';
    };
    // Get a logger handle
    logging.getLogger = function (name) {
        var logclass = 'log',
            level = 10,
            handlers = [],
            logger;
        if (name === undefined) {
            name = 'root';
        }
        logger = logging.loggers[name];
        if (logger !== undefined) {
            return logger;
        }
        logger = {
            'name': name,
            'level': function () {
                return level;
            },
            'set_level': function (lev) {
                level = parseInt(String(lev), 10);
            },
            'addHandler': function (h) {
                if (h !== undefined) {
                    if (h.formatter === undefined) {
                        h = {'formatter': logging.default_formatter,
                             'log': h};
                    }
                    handlers.push(h);
                }
            },
            'log': function (message, lvl) {
                if (lvl < level) {return; }
                $.each(handlers, function (i, handle) {
                    handle.log(handle.formatter(message, lvl));
                });
            }
        };
        // Add console handle
        if (console !== undefined && console.log !== undefined) {
            logger.addHandler(function (msg) {
                console.log(msg);
            });
        }
        // For each logging level add logging function
        $.each(logging.levels, function (name, level) {
            logger[name] = function (msg, e) {
                if (level.f) {
                    msg = level.f(msg, e);
                }
                logger.log(msg, level.level);
            };
        });
        // Add logger to the global loggers object
        logging.loggers[logger.name] = logger;
        return logger;
    };
    return logging;
}());
/**
 *
 * The global djpcms object
 */
$.djpcms = {
    widgets: {},
    // Base object for widgets
    base_widget: {
        _create: function () {
            return this;
        },
        factory: function () {
            return $.djpcms.widgets[this.name];
        },
        destroy: function () {
            var instances = this.factory().instances,
                idx = instances.indexOf(this.id),
                res;
            if (idx !== -1) {
                res = instances[idx];
                delete instances[idx];
                delete res.element[0].djpcms_widget;
                //res = widgets.instances.splice(idx, 1)[0];
            }
            return res;
        },
        ui: function (name, options_or_element, options) {
            return $.djpcms.ui[name](options_or_element, options);
        },
        tostring: function (msg) {
            if (msg) {
                msg = this.name + ' ' + this.id + ' - ' + msg;
            } else {
                msg = this.name + ' ' + this.id;
            }
            return msg;
        },
        debug: function (msg) {$.djpcms.logger.debug(this.tostring(msg)); },
        info: function (msg) {$.djpcms.logger.info(this.tostring(msg)); },
        warn: function (msg) {$.djpcms.logger.warn(this.tostring(msg)); },
        error: function (msg) {$.djpcms.logger.error(this.tostring(msg)); },
        critical: function (msg) {$.djpcms.logger.critical(this.tostring(msg)); }
    },
    // Base object for widget factories.
    widgetmaker: {
        name: 'widget',
        defaultElement: '<div>',
        selector: null,
        instance: function (id) {
            if (typeof id !== 'number') { id = id.id; }
            return this.instances[id];
        },
        options: function () {
            return $.djpcms.options[this.name];
        },
        // Create the widget on element
        create: function (element, options) {
            var maker = this,
                data = element.data('options') || element.data(),
                self,
                instance_id;
            self = $.extend({}, maker.factory);
            self.id = parseInt(maker.instances.push(self), 10) - 1;
            self.element = element;
            element[0].djpcms_widget = self;
            if (data) {
                options = $.extend(true, {}, options, data);
            }
            self.config = options;
            $.djpcms.logger.debug('Creating widget ' + self.name);
            self._create();
            return maker.instance(self.id);
        },
        // Given a jQuery object, build as many widgets
        make: function (elements, options) {
            var maker = this,
                wdgs = [],
                wdg;
            options = $.extend(true, {}, maker.options(), options);
            $.each(elements, function () {
                wdg = maker.create($(this), options);
                if (wdg !== undefined) {
                    wdgs.push(wdg);
                }
            });
            if (wdgs.length === 1) {
                wdgs = wdgs[0];
            }
            return wdgs;
        },
        decorate: function (container) {
            var selector = this.selector;
            if (selector) {
                if (container.is(selector)) {
                    this.make(container);
                }
                this.make($(selector, container));
            }
        },
        ui: function (options_or_element, options) {
            var element = options_or_element;
            if (options === undefined && $.isPlainObject(options_or_element)) {
                options = options_or_element;
                element = undefined;
            }
            element = $(element || this.defaultElement);
            return this.make(element, options);
        },
        create_ui: function () {
            var self = this;
            return function (options_or_element, options) {
                return self.ui(options_or_element, options);
            };
        }
    },
    ui: {
        name: 'djpcms',
        widget_head: 'ui-widget-header',
        widget_body: 'ui-widget-content',
        corner_top: 'ui-corner-top',
        corner_bottom: 'ui-corner-bottom',
        ui_input: 'ui-input',
        dialog: function (el, options) {
            var ui = $.djpcms.ui,
                open = true,
                wdg;
            options = options || {};
            if (options.autoOpen === false) {
                open = false;
            }
            options.autoOpen = false;
            wdg = el.dialog(options).dialog('widget');
            if (ui.icons === 'fontawesome') {
                $('.ui-dialog-titlebar-close', wdg)
                    .html('<i class="icon-remove"></i>')
                    .addClass(ui.classes.float_right);
            }
            if (open) {
                el.dialog('open');
            }
            return el;
        }
    }
};
/**
 * djpcms site manager
 */
$.djpcms = (function (djpcms) {
    // Private variables
    var actions = {},
        jsonCallBacks = {},
        inrequest = false,
        panel = null,
        appqueue = [],
        logger = $.logging.getLogger(),
        defaults = {
            media_url: "/media/",
            debug: false,
            remove_effect: {type: "drop", duration: 500},
            fadetime: 200
        };
    //
    function widgetmaker(deco, base_widget) {
        var base = base_widget || djpcms.widgetmaker,
            factory = base.factory || djpcms.base_widget;
        deco.factory = $.extend({}, factory, deco);
        deco.superClass = base_widget;
        deco.instances = [];
        $.each(base, function (name, value) {
            if (deco[name] === undefined) {
                deco[name] = value;
            }
        });
        return deco;
    }
    // Add a new decorator
    function addDecorator(deco) {
        var name = deco.name || djpcms.widgetmaker.name,
            base_widget = djpcms.widgets[name] || djpcms.widgets[djpcms.widgetmaker.name],
            config = deco.config;
        deco.name = name;
        if (config !== undefined) {
            delete deco.config;
        }
        if (defaults[name]) {
            config = $.extend(true, defaults[name], config);
        }
        defaults[name] = config;
        deco = widgetmaker(deco, base_widget);
        djpcms.widgets[name] = deco;
        djpcms.ui[name] = deco.create_ui();
    }
    // Set a logging panel
    function set_logging_pannel(panel) {
        panel = $(panel);
        if (panel.length) {
            logger.addHandler({
                formatter: $.logging.html_formatter,
                log: function (msg) {
                    panel.prepend(msg);
                }
            });
        }
    }
    // Create an object containing data to send to the server via AJAX.
    // *NAME* is the name of the interaction
    function ajaxparams(name, data) {
        var p = {'xhr': name};
        if (data) {
            p = $.extend(p, data);
        }
        return p;
    }
    //
    function queue_application(app) {
        if ($.data(document, 'djpcms')) {
            app();
        } else {
            appqueue.push(app);
        }
    }
    // Set options
    function setOptions(options) {
        $.extend(true, defaults, options);
    }
    // Add a new callback for JSON data
    function addJsonCallBack(jcb) {
        jsonCallBacks[jcb.id] = jcb;
    }
    // Remove a decorator
    function removeDecorator(rid) {
        if ($.djpcms.widgets.hasOwnMethod(rid)) {
            delete $.djpcms.widgets[rid];
        }
    }
    //
    function _jsonParse(data, elem) {
        var id  = data.header,
            jcb = jsonCallBacks[id];
        if (jcb) {
            return jcb.handle(data.body, elem, defaults);
        } else {
            logger.error('Could not find callback ' + id);
        }
    }
    // Add new action
    function addAction(id, action) {
        var a = actions[id];
        if (!a) {
            a = {'action': action, 'ids': {}};
            actions[id] = a;
        } else if (action) {
            a.action = action;
        }
        return a;
    }
    //
    function registerActionElement(actionid, id) {
        var action = addAction(actionid, null);
        action.ids[id] = id;
    }
    //
    function getAction(actionid, id) {
        var action = addAction(actionid, null);
        if (action.ids[id]) {
            delete action.ids[id];
            return action.action;
        }
    }
    /**
     * Handle a JSON call back by looping through all the callback
     * objects registered
     * @param data JSON object already unserialized
     * @param status String status flag
     * @param elem (Optional) jQuery object or HTMLObject
     */
    function _jsonCallBack(data, status, elem) {
        var v = false;
        if (status === "success") {
            v = _jsonParse(data, elem);
        }
        inrequest = false;
        return v;
    }
    /**
     * DJPCMS Handler constructor
     * It applys djpcms decorator to the element.
     */
    function _construct(elem) {
        return elem.each(function () {
            var me = $(this),
                config = defaults,
                lp = $('.djp-logging-panel', me),
                //parent = me.closest('.djpcms-loaded'),
                parent = [];
            //
            if (!parent.length) {
                if (this === document) {
                    me = $('body');
                }
                me.addClass('djpcms-loaded').trigger('djpcms-before-loading');
                if (lp) {
                    set_logging_pannel(lp);
                }
                $.each($.djpcms.widgets, function (name, widget) {
                    widget.decorate(me);
                });
                if (this === document) {
                    $.data(this, 'djpcms', config);
                    $.each(appqueue, function (i, app) {
                        app();
                    });
                    appqueue = [];
                }
                me.trigger('djpcms-after-loading');
            }
        });
    }
    //
    return $.extend(djpcms, {
        'construct': _construct,
        'options': defaults,
        'jsonParse': _jsonParse,
        'addJsonCallBack': addJsonCallBack,
        'jsonCallBack': _jsonCallBack,
        'decorator': addDecorator,
        'set_options': setOptions,
        'ajaxparams': ajaxparams,
        'set_inrequest': function (v) {inrequest = v; },
        'before_form_submit': [],
        'addAction': addAction,
        'registerActionElement': registerActionElement,
        'getAction': getAction,
        'inrequest': function () {return inrequest; },
        'logger': logger,
        'queue': queue_application,
        'panel': function () {
            // A floating panel
            if (!panel) {
                panel = $('<div>').hide().appendTo($('body'))
                                .addClass('float-panel ui-widget ui-widget-content ui-corner-all')
                                .css({position: 'absolute',
                                     'text-align': 'left',
                                      padding: '5px'});
            }
            return panel;
        },
        'smartwidth': function (html) {
            return Math.max(15 * Math.sqrt(html.length), 200);
        }
    });
}($.djpcms));
//
// BASE WIDGET
$.djpcms.decorator({
    config: {
        classes: {
            widget: 'ui-widget',
            head: 'ui-widget-header',
            body: 'ui-widget-content',
            foot: 'ui-widget-footer',
            active: 'ui-state-active',
            clickable: 'ui-clickable',
            float_right: 'f-right'
        }
    }
});


$.djpcms.confirmation_dialog = function (title, html, callback, opts) {
    var el = $('<div title="' + title + '"></div>').html(String(html)),
        options = $.extend({}, opts, {
            modal: true,
            draggable: false,
            resizable: false,
            buttons: {
                Ok: function () {
                    $(this).dialog("close");
                    callback(true);
                },
                Cancel: function () {
                    $(this).dialog("close");
                    callback(false);
                }
            },
            close: function (event, ui) {
                el.dialog('destroy').remove();
            }
        });
    return $.djpcms.ui.dialog(el, options);
};
// Warning dialog
$.djpcms.warning_dialog = function (title, warn, callback) {
    var opts = {
            dialogClass: 'ui-state-error',
            autoOpen: false
        },
        el = $.djpcms.confirmation_dialog(title, warn, callback, opts);
    $('.ui-dialog-titlebar, .ui-dialog-buttonpane', el.dialog('widget'))
                .addClass('ui-state-error');
    el.dialog("open");
    return el;
};
/**
 *  DJPCMS AJAX DATA LOADER CLOSURE.
 *
 *  An utility which return a function which can be used to
 *  perform AJAX requests with confirmation and callbacks handled
 *  by djpcms callbacks.
 *
 *  For example
 *
 *  myloader = $.djpcms.ajax_loader('/my/path/','reload','post')
 *  myloader()
 *
 */
$.djpcms.ajax_loader =  function djpcms_loader(url, action, method, data, conf) {
    var sendrequest = function (callback) {
        var that = this;
        if (conf && !callback) {
            $('<div></div>').html(conf).dialog({
                modal: true,
                draggable: false,
                resizable: false,
                buttons: {
                    Ok: function () {
                        $(this).dialog("close");
                        sendrequest(true);
                    },
                    Cancel: function () {
                        $(this).dialog("close");
                        $.djpcms.set_inrequest(false);
                    }
                }
            });
        } else {
            $.ajax({
                'url': url,
                'type': method || 'post',
                'dataType': 'json',
                'success': function (e, s) {
                    $.djpcms.set_inrequest(false);
                    $.djpcms.jsonCallBack(e, s, that);
                },
                'data': $.djpcms.ajaxparams(action, data)
            });
        }
    };
    return sendrequest;
};
//
$.djpcms.ajax_loader_from_tool = function (tool) {
    if (tool.ajax) {
        return $.djpcms.ajax_loader(tool.url,
                                    tool.action,
                                    tool.method,
                                    tool.data,
                                    tool.conf);
    }
};
/**
 * A modal error dialog
 */
$.djpcms.errorDialog = function (html, title) {
    title = title || 'Something did not work';
    var el = $('<div title="' + title + '"></div>').html(String(html)),
        width = $.djpcms.smartwidth(html);
    el.dialog({modal: true,
               autoOpen: false,
               dialogClass: 'ui-state-error',
               'width': width});
    $('.ui-dialog-titlebar', el.dialog('widget')).addClass('ui-state-error');
    el.dialog("open");
};
/**
 *
 * JSON CALLBACKS
 */
$.djpcms.addJsonCallBack({
    id: "error",
    handle: function (data, elem) {
        $.djpcms.errorDialog(data);
    }
});
//
$.djpcms.addJsonCallBack({
    id: "servererror",
    handle: function (data, elem) {
        $.djpcms.errorDialog(data, "Unhandled Server Error");
    }
});
//
$.djpcms.addJsonCallBack({
    id: "message",
    handle: function (data, elem) {
        $.djpcms.logger.info(data);
        return true;
    }
});
//
$.djpcms.addJsonCallBack({
    id: "empty",
    handle: function (data, elem) {
        return true;
    }
});
/**
 * collection callback
 */
$.djpcms.addJsonCallBack({
    id: "collection",
    handle: function (data, elem) {
        $.each(data, function (i, component) {
            $.djpcms.jsonParse(component, elem);
        });
        return true;
    }
});
/**
 * html JSON callback. The server returns a list of objects with
 * a selctor and html attributes which are going to be
 * added/replaced to the document
 */
$.djpcms.addJsonCallBack({
    id: "htmls",
    handle: function (data, elem, config) {
        $.each(data, function (i, b) {
            var el = $(b.identifier, elem),
                fade = config.fadetime,
                html;
            if (!el.length && b.alldocument) {
                el = $(b.identifier);
            }
            if (el.length) {
                if (b.type === 'hide') {
                    el.hide();
                } else if (b.type === 'show') {
                    el.show();
                } else if (b.type === 'value') {
                    el.val(b.html);
                } else if (b.type === 'append') {
                    $(b.html).djpcms().appendTo(el);
                } else {
                    html = $(b.html).djpcms();
                    el.show();
                    el.fadeOut(fade, 'linear', function () {
                        if (b.type === 'replacewith') {
                            el.replaceWith(html);
                        } else {
                            if (b.type === 'addto') {
                                el.append(html);
                            } else {
                                // The append method does not seems to
                                // presenve events on html. So I use this
                                // hack.
                                var tmp = $('<div></div>');
                                el.empty().append(tmp);
                                tmp.replaceWith(html);
                            }
                        }
                        el.fadeIn(fade);
                    });
                }
            }
        });
        return true;
    }
});
/**
 * attribute JSON callback
 */
$.djpcms.addJsonCallBack({
    id: "attribute",
    handle: function (data, elem) {
        var selected = [];
        $.each(data, function (i, b) {
            var el;
            if (b.alldocument) {
                el = $(b.selector);
            } else {
                el = $(b.selector, elem);
            }
            if (el.length) {
                b.elem = el;
            }
        });
        $.each(data, function (i, b) {
            if (b.elem) {
                b.elem.attr(b.attr, b.value);
            }
        });
    }
});
/**
 * Remove html elements
 */
$.djpcms.addJsonCallBack({
    id: "remove",
    handle: function (data, elem) {
        $.each(data, function (i, b) {
            var el = $(b.identifier, elem),
                be = $.djpcms.options.remove_effect;
            if (!el.length && b.alldocument) {
                el = $(b.identifier);
            }
            if (el.length) {
                el.fadeIn(be.duration, function () {el.remove(); });
                //el.hide(be.type,{},be.duration,function() {el.remove();});
            }
        });
        return true;
    }
});
/**
 * Redirect
 */
$.djpcms.addJsonCallBack({
    id: "redirect",
    handle: function (data, elem) {
        window.location = data;
    }
});
/**
 * Dialog callback
 *
 * Create a jQuery dialog from JSON data
 */
$.djpcms.addJsonCallBack({
    id: "dialog",
    handle: function (data, elem) {
        var el = $('<div></div>').html(data.html).djpcms(),
            buttons = {},
            options = data.options;
        $.each(data.buttons, function (n, b) {
            buttons[b.name] = function () {
                b.d = $(this);
                b.dialogcallBack = function (data) {
                    $.djpcms.jsonCallBack(data, 'success', el);
                    if (b.close) {
                        b.d.dialog("close");
                    }
                };
                if (b.url) {
                    var params = $('form', el).formToArray(),
                        extra;
                    if (b.func) {
                        extra = $.djpcms.ajaxparams(b.func);
                        $.each(extra, function (k, v) {
                            params.push({'name': k, 'value': v});
                        });
                    }
                    $.post(b.url,
                            $.param(params),
                            b.dialogcallBack,
                            "json");
                } else {
                    b.d.dialog('close');
                }
            };
        });
        options.buttons = buttons;
        el.dialog(options);
        return el;
    }
});

/**
 * Format a number and return a string based on input settings
 * @param {Number} number The input number to format
 * @param {Number} decimals The amount of decimals
 * @param {String} decPoint The decimal point, defaults to the one given in the lang options
 * @param {String} thousandsSep The thousands separator, defaults to the one given in the lang options
 */
//$.djpcms.numberFormat = function (number, decimals, decPoint, thousandsSep) {
//    var lang = defaultOptions.lang,
//        // http://kevin.vanzonneveld.net/techblog/article/javascript_equivalent_for_phps_number_format/
//        n = number, c = isNaN(decimals = mathAbs(decimals)) ? 2 : decimals,
//        d = decPoint === undefined ? lang.decimalPoint : decPoint,
//        t = thousandsSep === undefined ? lang.thousandsSep : thousandsSep, s = n < 0 ? "-" : "",
//        i = String(pInt(n = mathAbs(+n || 0).toFixed(c))),
//        j = i.length > 3 ? i.length % 3 : 0;
//
//    return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) +
//        (c ? d + mathAbs(n - i).toFixed(c).slice(2) : "");
//};
/**
 * Return an object containing the formatted currency and a flag
 * indicating if it is negative
 */
$.djpcms.format_currency = function (s, precision) {
    if (!precision) {
        precision = 3;
    }
    s = s.replace(/, /g, '');
    var c = parseFloat(s),
        isneg = false,
        decimal = false,
        de = '',
        i,
        cs,
        cn,
        d,
        k,
        N,
        mul,
        atom;
    //
    if (isNaN(c)) {
        cs = s;
    } else {
        cs = s.split('.', 2);
        if (c < 0) {
            isneg = true;
            c = Math.abs(c);
        }
        cn = parseInt(c, 10);
        if (cs.length === 2) {
            de = cs[1];
            if (!de) {
                de = '.';
            } else {
                decimal = true;
                de = c - cn;
            }
        }
        if (decimal) {
            mul = Math.pow(10, precision);
            atom = String(parseInt(c * mul, 10) / mul).split(".")[1];
            de = '';
            decimal = false;
            for (i = 0; i < Math.min(atom.length, precision); i++) {
                de += atom[i];
                if (parseInt(atom[i], 10) > 0) {
                    decimal = true;
                }
            }
            if (decimal) {
                de = '.' + de;
            }
        }
        cn += "";
        N  = cn.length;
        cs = "";
        for (i = 0; i < N; i++) {
            cs += cn[i];
            k = N - i - 1;
            d = parseInt(k / 3, 10);
            if (3 * d === k && k > 0) {
                cs += ',';
            }
        }
        cs += de;
        if (isneg) {
            cs = '-' + cs;
        } else {
            cs = String(cs);
        }
    }
    return {
        value: cs,
        negative: isneg
    };
};
/**
 * Ajax links, buttons, select and forms
 *
 * Decorate elements for jQuery ui if the jquery flag is true (default).
 * and apply ajax functionality where required.
 */
$.djpcms.decorator({
    name: "ajax",
    description: "add ajax functionality to links, buttons, selects and forms",
    defaultElement: '<a>',
    selector: 'a.ajax, button.ajax, select.ajax, form.ajax, input.ajax',
    config: {
        dataType: "json",
        classes: {
            submit: 'submitted',
            autoload: "autoload"
        },
        confirm_actions: {
            'delete': 'Please confirm delete',
            'flush': 'Please confirm flush'
        },
        effect: {
            name: 'fade',
            options: {},
            speed: 50
        },
        form: {
            iframe: false,
            beforeSerialize: function (jqForm, opts) {
                return true;
            },
            beforeSubmit: function (formData, jqForm, opts) {
                var self = jqForm[0].djpcms_widget,
                    ok = !self.disabled;
                if (ok) {
                    self.disabled = true;
                    $.each($.djpcms.before_form_submit, function () {
                        formData = this(formData, jqForm);
                    });
                    jqForm.addClass(self.config.classes.submit);
                }
                return ok;
            },
            success: function (o, s, xhr, jqForm) {
                var self = jqForm[0].djpcms_widget;
                return self.finished(o, s, xhr);
            },
            error: function (o, s, xhr, jqForm) {
                var self = jqForm[0].djpcms_widget;
                return self.finished(o, s, xhr);
            }
        },
        timeout: 30
    },
    _create: function () {
        var self = this,
            element = self.element;
        self.disabled = false;
        if (element.is('select')) {
            self.type = 'select';
            self.create_select();
        } else if (element.is('input')) {
            self.type = 'input';
            self.create_select();
        } else if (element.is('form')) {
            self.type = 'form';
            self.create_form();
        } else {
            self.type = 'link';
            self.create_link();
        }
    },
    finished: function (o, s, xhr) {
        var self = this,
            jqForm = self.element,
            effect = self.config.effect,
            matched = $('.form-messages, .error', jqForm),
            processed = 0;
        jqForm.removeClass(self.config.classes.submit);
        self.disabled = false;
        matched.hide(effect.name, effect.options, effect.speed, function () {
            processed += 1;
            $(this).html('').show();
            if (processed === matched.length) {
                $.djpcms.jsonCallBack(o, s, jqForm);
            }
        });
    },
    form_data: function () {
        var elem = this.element,
            form = elem.closest('form'),
            data = {
                conf: elem.data('warning'),
                name: elem.attr('name'),
                url: elem.attr('href') || elem.data('href'),
                type: elem.data('method') || 'get',
                submit: elem.data('submit')
            };
        if (form.length === 1) {
            data.form = form;
        }
        if (!data.url && data.form) {
            data.url = data.form.attr('action');
        }
        if (!data.url) {
            data.url = window.location.toString();
        }
        return data;
    },
    // Submit data via ajax
    submit: function (data) {
        var self = this;
        //
        function loader(ok) {
            if (ok) {
                var submit_data = $.djpcms.ajaxparams(data.name, data.submit),
                    opts = {
                        url: data.url,
                        type: data.type,
                        dataType: self.config.dataType,
                        data: submit_data
                    };
                self.info('Submitting ajax ' + opts.type + ' request "' + data.name + '"');
                if (!data.form) {
                    opts.data.value = self.element.val();
                    opts.success = $.djpcms.jsonCallBack;
                    $.ajax(opts);
                } else {
                    $.extend(opts, self.config.form);
                    //data.form[0].clk = self.element[0];
                    data.form.ajaxSubmit(opts);
                }
            }
        }
        if (data.conf) {
            $.djpcms.warning_dialog(data.conf.title || '', data.conf.body || data.conf, loader);
        } else {
            loader(true);
        }
    },
    create_select: function () {
        var self = this,
            data = self.form_data();
        self.element.change(function (event) {
            self.submit(data);
        });
    },
    create_link: function () {
        var self = this,
            data = self.form_data();
        self.element.click(function (event) {
            event.preventDefault();
            self.submit(data);
        });
    },
    create_form: function () {
        var self = this,
            form = self.element,
            opts = {
                url: form.attr('action'),
                type: form.attr('method'),
                dataType: self.config.dataType
            },
            name;
        $.extend(opts, self.config.form);
        form.ajaxForm(opts);
        if (form.hasClass(self.config.classes.autoload)) {
            name = form.attr("name");
            form[0].clk = $(":submit[name='" + name + "']", form)[0];
            form.submit();
        }
    }
});
/**
 * AUTOCOMPLETE
 *
 * The actual values are stored in the data attribute of the input element.
 * The positioning is with respect the "widgetcontainer" parent element if
 * available.
 */
$.djpcms.decorator({
    name: "autocomplete",
    defaultElement: '<input>',
    selector: 'input.autocomplete',
    config: {
        classes: {
            autocomplete: 'autocomplete',
            list: 'multiSelectList',
            container: 'multiSelectContainer'
        },
        removelink: function (self) {
            return $('<a href="#"><i class="icon-remove"></i></a>');
        },
        minLength: 2,
        maxRows: 50,
        search_string: 'q',
        separator: ', ',
        multiple: false
    },
    split: function (val) {
        return val.split(/,\s*/);
    },
    // Callback received when an element is selected
    add_data: function (item) {
        var self = this;
        if (self.config.multiple) {
            self.addOption(item);
        } else {
            self.real.val(item.real_value);
            self.element.val(item.value);
            //this.real.data('value', item.value);
        }
        return false;
    },
    get_autocomplete_data: function (jform, options, veto) {
        var value = this.element.val();
        if(this.multiple) {
            //
        } else {
            if (this.real.data('value') !== value) {
                this.real.val(value);
            }
        }
    },
    // Add a new option to the multiselect element
    addOption: function (elem) {
        var self = this,
            list = self.list,
            selections = list.data('selections'),
            options = self.config,
            item = $('<li>'),
            opt = $('<option>', {
                text: elem.label,
                val: elem.real_value
            }),
            val = opt.val();
        if (selections.indexOf(val) === -1) {
            self.real.append(opt);
            selections.push(val);
            item.append($('<span>', {html: elem.label}))
                .append(options.removelink(self))
                .data('option', opt).appendTo(self.list);
            if (self.list.children().length) {
                self.list_container.show();
            }
            opt.prop('selected', true);
            self.element.val('');
        }
    },
    //
    dropListItem: function (li) {
        var opt = li.data('option'),
            selections = this.list.data('selections'),
            idx;
        li.remove();
        if (this.list.children().length === 0) {
            this.list_container.hide();
        }
        idx = selections.indexOf(opt.val());
        if (idx !== -1) {
            selections.splice(idx, 1);
        }
        opt.remove();
    },
    //
    buildDom: function () {
        var self = this,
            options = self.config,
            classes = $.djpcms.options.input.classes,
            container = $('<div>', {'class': options.classes.container}),
            list = self.list;
        if (self.wrapper) {
            self.wrapper.after(container);
            container.addClass(classes.control)
                     .prepend(self.wrapper.removeClass(classes.control));
            list = $('<div>', {'class': classes.input}).addClass(options.classes.container).append(self.list);
        } else {
            //container.prepend(element.after(container));
        }
        self.list_container = list.hide();
        container.append(self.list_container);
    },
    //
    _create: function () {
        var self = this,
            opts = self.config,
            elem = this.element,
            name = elem.attr('name'),
            name_len = name.length;
        opts.select = function (event, ui) {
            return self.add_data(ui.item);
        };
        self.wrapper = elem.parent('.' + $.djpcms.options.input.classes.input);
        if(!self.wrapper.length) {
            self.wrapper = null;
        }
        opts.position = {of: self.wrapper || elem};
        // Build the real (hidden) input
        if(opts.multiple) {
            if (name.substring(name_len-2, name_len) === '[]') {
                name = name.substring(0, name_len-2);
            }
            self.real = $('<select name="'+ name +'[]" multiple="multiple"></select>');
            self.list = $('<ul>').data('selections', []).addClass(opts.classes.list);
            self.buildDom();
            //
            self.list.delegate('a', 'click', function(e) {
                e.preventDefault();
                self.dropListItem($(this).closest('li'));
                return false;
            });
            //
            opts.focus = function() {
                return false;
            };
            elem.bind("keydown", function( event ) {
                if ( event.keyCode === $.ui.keyCode.TAB &&
                        $( this ).data( "autocomplete" ).menu.active ) {
                    event.preventDefault();
                }
            });
        } else {
            self.real = $('<input name="'+ name +'"></input>');
        }
        elem.attr('name', name + '_proxy').before(self.real.hide());
        if (opts.initials_value) {
            $.each(opts.initials_value, function(i, initial) {
                self.add_data({real_value: initial[0], value: initial[1]});
            });
        }
        // If choices are available, it is a local autocomplete.
        if (opts.choices && opts.choices.length) {
            var sources = [];
            $.each(opts.choices, function(i, val) {
                sources[i] = {value:val[0], label:val[1]};
            });
            opts.source = function( request, response ) {
                if(opts.multiple) {
                    throw('Not implemented');
                    //response( $.ui.autocomplete.filter(
                    //    sources, split(request.term).pop() ) );
                }
                else {
                    return sources;
                }
            };
            elem.autocomplete(opts);
        } else if(opts.url) {
            // We have a url, the data is obtained remotely.
            opts.source = function(request, response) {
                var ajax_data = {
                        style: 'full',
                        maxRows: opts.maxRows,
                        'search_string': opts.search_string
                    },
                    loader;
                ajax_data[opts.search_string] = request.term;
                loader = $.djpcms.ajax_loader(opts.url, 'autocomplete', 'get', ajax_data);
                $.proxy(loader, response)();
            };
            elem.autocomplete(opts);
        } else {
            self.warn('Could not find choices or url for autocomplete data');
        }
    }
});
//
$.djpcms.addJsonCallBack({
    id: "autocomplete",
    handle: function (data, response) {
        response($.map(data, function (item) {
            return {
                value: item[0],
                label: item[1],
                real_value: item[2]
            };
        }));
    }
});

/**
 * Simulate a readonly select widget
 */
$.djpcms.decorator({
    name: 'readonly',
    defaultElement: '<select>',
    selector: 'select.readonly',
    _create: function() {
        var elem = this.element,
            selected = $(':selected', elem);
        elem.change(function () {
            elem.children().prop('selected', false);
            selected.prop('selected', true);
        });
    }
});
//
$.djpcms.decorator({
    name: 'input',
    defaultElement: '<input type="text">',
    selector: '.ui-input',
    config: {
        // If true, the input can submit the form when ENTER is pressed on it.
        submit: false,
        classes: {
            input: 'ui-input',
            control: 'control',
            focus: 'focus'
        }
    },
    _create: function () {
        var self = this,
            elem = self.element,
            config = self.config,
            prev;
        if (elem.is('input') || elem.is('textarea')) {
            // Create the wrapper
            elem.removeClass(config.classes.input);
            self.wrapper = $('<div></div>').addClass(config.classes.input);
            prev = elem.prev();
            if (prev.length) {
                prev.after(self.wrapper);
            } else {
                prev = elem.parent();
                if (prev.length) {
                    prev.prepend(self.wrapper);
                }
            }
            self.wrapper.append(elem).addClass(elem.attr('name'));
        } else {
            self.wrapper = elem;
            elem = self.wrapper.children('input,textarea');
            if (elem.length === 1) {
                $.extend(true, config, elem.data('options'));
                self.element = elem;
            }
        }
        self.element.focus(function () {
            self.wrapper.addClass(config.classes.focus);
        }).blur(function () {
            self.wrapper.removeClass(config.classes.focus);
        });
        // If the element has the submit-on-enter class, add
        // the keypressed event on ENTER to submit the form
        if (config.submit) {
            self.element.keypress(function (e) {
                if (e.which === 13) {
                    var form = elem.closest('form');
                    if (form.length) {
                        form.submit();
                    }
                }
            });
        }
    }
});
//
/*
 * Add an icon to the element.
 */
$.djpcms.decorator({
    name: 'icon',
    defaultElement: 'i',
    sources: {
        fontawesome: function (self, icon) {
            if (!icon) {
                icon = 'icon-question-sign';
            } else if (icon.substring(0, 5) !== 'icon-') {
                icon = 'icon-' + icon;
            }
            self.element.prepend('<i class="' + icon + '"></i>');
        }
    },
    config: {
        source: 'fontawesome'
    },
    _create: function () {
        var config = this.config,
            source = this.sources[config.source],
            icon = config.icon;
        if (source) {
            if ($.isPlainObject(icon)) {
                icon = icon[config.source];
            }
            source(this, icon);
        }
    }
});
//
$.djpcms.decorator({
    name: 'button',
    defaultElement: '<button>',
    description: 'Add button like functionalities to html objects. It can handle anchors, buttons, inputs and checkboxes',
    selector: '.btn',
    config: {
        disabled: null,
        text: true,
        icon: null,
        classes: {
            button: 'btn',
            button_small: 'btn-small',
            button_large: 'btn-large',
            button_group: 'btn-group'
        }
    },
    _create: function () {
        var self = this,
            element = self.element.hide(),
            options = self.config,
            classes = options.classes,
            buttonElement,
            labelSelector,
            ancestor,
            toggle,
            children;
        if (element.is("[type=checkbox]")) {
            self.type = "checkbox";
        } else if (element.is("[type=radio]")) {
            self.type = "radio";
        } else if (element.is("input")) {
            self.type = "input";
        } else {
            self.type = "button";
        }
        // This is a checkbox
        if (self.type === "checkbox" || self.type === "radio") {
            toggle = true;
            labelSelector = "label[for='" + element.attr('id') + "']";
            ancestor = element.parents().last();
            buttonElement = ancestor.find(labelSelector);
            if (buttonElement) {
                element.removeClass(classes.button);
                buttonElement.attr('title', buttonElement.html());
            }
        } else {
            buttonElement = element;
        }
        if (buttonElement) {
            self.buttonElement = buttonElement;
            children = buttonElement.children();
            if (!options.text) {
                buttonElement.html('');
            } else if (options.text !== true) {
                buttonElement.html(options.text);
            }
            if (options.icon) {
                self.ui('icon', buttonElement, {icon: options.icon});
            }
            buttonElement.addClass(classes.button).css('display', 'inline-block');
            if (toggle) {
                self.refresh();
                element.bind('change', function () {
                    self.refresh();
                });
            }
        } else {
            self.destroy();
        }
    },
    refresh: function () {
        var self = this,
            classes = $.djpcms.options.widget.classes;
        if (self.element.prop("checked")) {
            $.djpcms.logger.debug('checked');
            self.buttonElement.addClass(classes.active);
        } else {
            $.djpcms.logger.debug('unchecked');
            self.buttonElement.removeClass(classes.active);
        }
    }
});
//
/*
 * Decorator for adding a remove link to alert messages.
 */
$.djpcms.decorator({
    name: 'alert',
    selector: '.alert',
    config: {
        dismiss: true,
        icon: {fontawesome: 'remove'},
        effect: {
            name: 'fade',
            options: {},
            speed: 400
        },
        float: 'right'
    },
    _create: function () {
        var self = this,
            opts = self.config,
            effect = opts.effect,
            a = $("<a href='#'>")
                .css({'float': opts.float}).click(function (e) {
                    e.preventDefault();
                    self.element.hide(effect.name, effect.options, effect.speed, function () {
                        $(this).remove();
                    });
                });
        $.djpcms.ui.icon(a, opts);
        self.element.append(a);
    }
});
$.djpcms.decorator({
    name: "collapsable",
    description: "Decorate box elements",
    selector: 'a.collapse',
    config: {
        classes: {
            collapsable: 'bd'
        },
        effect: {
            type: 'blind',
            options: {},
            duration: 10
        },
        icons: {
            open: {
                fontawesome: 'plus-sign'
            },
            close: {
                fontawesome: 'minus-sign'
            }
        }
    },
    _create: function () {
        var self = this,
            classes = $.djpcms.options.widget.classes;
        self.widget = self.element.closest('.' + classes.widget);
        self.body = self.widget.find('.' + self.config.classes.collapsable).first();
        if(self.body.length) {
            self.toggle();
            self.element.mousedown(function (e) {
                e.stopPropagation();
            }).click(function () {
                self.widget.toggleClass('collapsed');
                self.toggle();
                return false;
            });
        }
    },
    toggle: function () {
        var self = this,
            be = self.config.effect,
            icons = self.config.icons,
            el = self.element.html('');
        if (self.widget.hasClass('collapsed')) {
            self.body.hide(be.type, be.options, be.duration, function () {
                $.djpcms.ui.icon(el, {icon: icons.open});
            });
            self.info('closed body');
        } else {
            self.body.show(be.type, be.options, be.duration, function () {
                $.djpcms.ui.icon(el, {icon: icons.close});
            });
            self.info('opened body');
        }
    }
});
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
/*globals Showdown*/
$.djpcms.decorator({
    name: "showdown",
    selector: '.markdown',
    _create: function () {
        var md = this.config.markdown,
            converter;
        if(md && Showdown) {
            converter = new Showdown.converter();
            md = converter.makeHtml(md);
        }
        this.element.html(md);
    }
});
/**
 * Common Ancestor jQuery plugin
 */
$.fn.commonAncestor = function () {
    if (!this.length) {
        return $([]);
    }
    var parents = [],
        minlen = Infinity,
        i,
        j,
        p,
        equal;
    //
    this.each(function () {
        var curparents = $(this).parents();
        parents.push(curparents);
        minlen = Math.min(minlen, curparents.length);
    });
    //
    $.each(parents, function (i, p) {
        parents[i] = p.slice(p.length - minlen);
    });
    // Iterate until equality is found
    for (i = 0; i < parents[0].length; i++) {
        p = parents[0][i];
        equal = true;
        for (j = 1; j < parents.length; j++) {
            if (parents[j][i] !== p) {
                equal = false;
                break;
            }
        }
        if (equal) {
            return $(p);
        }
    }
    return $([]);
};
// extend plugin scope
$.fn.extend({
    djpcms: function () {
        return $.djpcms.construct(this);
    }
});
}(jQuery));