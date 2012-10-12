(function(e){"use strict";function n(t){var n=t.data;t.isDefaultPrevented()||(t.preventDefault(),e(this).ajaxSubmit(n))}function r(t){var n=t.target,r=e(n);if(!r.is(":submit,input:image")){var i=r.closest(":submit");if(i.length===0)return;n=i[0]}var s=this;s.clk=n;if(n.type=="image")if(t.offsetX!==undefined)s.clk_x=t.offsetX,s.clk_y=t.offsetY;else if(typeof e.fn.offset=="function"){var o=r.offset();s.clk_x=t.pageX-o.left,s.clk_y=t.pageY-o.top}else s.clk_x=t.pageX-n.offsetLeft,s.clk_y=t.pageY-n.offsetTop;setTimeout(function(){s.clk=s.clk_x=s.clk_y=null},100)}function i(){if(!e.fn.ajaxSubmit.debug)return;var t="[jquery.form] "+Array.prototype.join.call(arguments,"");window.console&&window.console.log?window.console.log(t):window.opera&&window.opera.postError&&window.opera.postError(t)}var t={};t.fileapi=e("<input type='file'/>").get(0).files!==undefined,t.formdata=window.FormData!==undefined,e.fn.ajaxSubmit=function(n){function x(t){var r=new FormData;for(var i=0;i<t.length;i++)r.append(t[i].name,t[i].value);if(n.extraData)for(var s in n.extraData)n.extraData.hasOwnProperty(s)&&r.append(s,n.extraData[s]);n.data=null;var o=e.extend(!0,{},e.ajaxSettings,n,{contentType:!1,processData:!1,cache:!1,type:"POST"});n.uploadProgress&&(o.xhr=function(){var e=jQuery.ajaxSettings.xhr();return e.upload&&(e.upload.onprogress=function(e){var t=0,r=e.loaded||e.position,i=e.total;e.lengthComputable&&(t=Math.ceil(r/i*100)),n.uploadProgress(e,r,i,t)}),e}),o.data=null;var u=o.beforeSend;o.beforeSend=function(e,t){t.data=r,u&&u.call(t,e,n)},e.ajax(o)}function T(t){function x(e){var t=e.contentWindow?e.contentWindow.document:e.contentDocument?e.contentDocument:e.document;return t}function C(){function o(){try{var e=x(d).readyState;i("state = "+e),e&&e.toLowerCase()=="uninitialized"&&setTimeout(o,50)}catch(t){i("Server abort: ",t," (",t.name,")"),M(S),b&&clearTimeout(b),b=undefined}}var t=u.attr("target"),n=u.attr("action");s.setAttribute("target",h),r||s.setAttribute("method","POST"),n!=f.url&&s.setAttribute("action",f.url),!f.skipEncodingOverride&&(!r||/post/i.test(r))&&u.attr({encoding:"multipart/form-data",enctype:"multipart/form-data"}),f.timeout&&(b=setTimeout(function(){y=!0,M(E)},f.timeout));var a=[];try{if(f.extraData)for(var l in f.extraData)f.extraData.hasOwnProperty(l)&&a.push(e('<input type="hidden" name="'+l+'">').attr("value",f.extraData[l]).appendTo(s)[0]);f.iframeTarget||(p.appendTo("body"),d.attachEvent?d.attachEvent("onload",M):d.addEventListener("load",M,!1)),setTimeout(o,15),s.submit()}finally{s.setAttribute("action",n),t?s.setAttribute("target",t):u.removeAttr("target"),e(a).remove()}}function M(t){if(v.aborted||O)return;try{L=x(d)}catch(n){i("cannot access response document: ",n),t=S}if(t===E&&v){v.abort("timeout");return}if(t==S&&v){v.abort("server abort");return}if(!L||L.location.href==f.iframeSrc)if(!y)return;d.detachEvent?d.detachEvent("onload",M):d.removeEventListener("load",M,!1);var r="success",s;try{if(y)throw"timeout";var o=f.dataType=="xml"||L.XMLDocument||e.isXMLDoc(L);i("isXml="+o);if(!o&&window.opera&&(L.body===null||!L.body.innerHTML)&&--A){i("requeing onLoad callback, DOM not available"),setTimeout(M,250);return}var u=L.body?L.body:L.documentElement;v.responseText=u?u.innerHTML:null,v.responseXML=L.XMLDocument?L.XMLDocument:L,o&&(f.dataType="xml"),v.getResponseHeader=function(e){var t={"content-type":f.dataType};return t[e]},u&&(v.status=Number(u.getAttribute("status"))||v.status,v.statusText=u.getAttribute("statusText")||v.statusText);var a=(f.dataType||"").toLowerCase(),l=/(json|script|text)/.test(a);if(l||f.textarea){var h=L.getElementsByTagName("textarea")[0];if(h)v.responseText=h.value,v.status=Number(h.getAttribute("status"))||v.status,v.statusText=h.getAttribute("statusText")||v.statusText;else if(l){var m=L.getElementsByTagName("pre")[0],g=L.getElementsByTagName("body")[0];m?v.responseText=m.textContent?m.textContent:m.innerText:g&&(v.responseText=g.textContent?g.textContent:g.innerText)}}else a=="xml"&&!v.responseXML&&v.responseText&&(v.responseXML=_(v.responseText));try{k=P(v,a,f)}catch(t){r="parsererror",v.error=s=t||r}}catch(t){i("error caught: ",t),r="error",v.error=s=t||r}v.aborted&&(i("upload aborted"),r=null),v.status&&(r=v.status>=200&&v.status<300||v.status===304?"success":"error"),r==="success"?(f.success&&f.success.call(f.context,k,"success",v),c&&e.event.trigger("ajaxSuccess",[v,f])):r&&(s===undefined&&(s=v.statusText),f.error&&f.error.call(f.context,v,r,s),c&&e.event.trigger("ajaxError",[v,f,s])),c&&e.event.trigger("ajaxComplete",[v,f]),c&&!--e.active&&e.event.trigger("ajaxStop"),f.complete&&f.complete.call(f.context,v,r),O=!0,f.timeout&&clearTimeout(b),setTimeout(function(){f.iframeTarget||p.remove(),v.responseXML=null},100)}var s=u[0],o,a,f,c,h,p,d,v,m,g,y,b,w=!!e.fn.prop;if(e(":input[name=submit],:input[id=submit]",s).length){alert('Error: Form elements must not have name or id of "submit".');return}if(t)for(a=0;a<l.length;a++)o=e(l[a]),w?o.prop("disabled",!1):o.removeAttr("disabled");f=e.extend(!0,{},e.ajaxSettings,n),f.context=f.context||f,h="jqFormIO"+(new Date).getTime(),f.iframeTarget?(p=e(f.iframeTarget),g=p.attr("name"),g?h=g:p.attr("name",h)):(p=e('<iframe name="'+h+'" src="'+f.iframeSrc+'" />'),p.css({position:"absolute",top:"-1000px",left:"-1000px"})),d=p[0],v={aborted:0,responseText:null,responseXML:null,status:0,statusText:"n/a",getAllResponseHeaders:function(){},getResponseHeader:function(){},setRequestHeader:function(){},abort:function(t){var n=t==="timeout"?"timeout":"aborted";i("aborting upload... "+n),this.aborted=1,p.attr("src",f.iframeSrc),v.error=n,f.error&&f.error.call(f.context,v,n,t),c&&e.event.trigger("ajaxError",[v,f,n]),f.complete&&f.complete.call(f.context,v,n)}},c=f.global,c&&0===e.active++&&e.event.trigger("ajaxStart"),c&&e.event.trigger("ajaxSend",[v,f]);if(f.beforeSend&&f.beforeSend.call(f.context,v,f)===!1){f.global&&e.active--;return}if(v.aborted)return;m=s.clk,m&&(g=m.name,g&&!m.disabled&&(f.extraData=f.extraData||{},f.extraData[g]=m.value,m.type=="image"&&(f.extraData[g+".x"]=s.clk_x,f.extraData[g+".y"]=s.clk_y)));var E=1,S=2,T=e("meta[name=csrf-token]").attr("content"),N=e("meta[name=csrf-param]").attr("content");N&&T&&(f.extraData=f.extraData||{},f.extraData[N]=T),f.forceSync?C():setTimeout(C,10);var k,L,A=50,O,_=e.parseXML||function(e,t){return window.ActiveXObject?(t=new ActiveXObject("Microsoft.XMLDOM"),t.async="false",t.loadXML(e)):t=(new DOMParser).parseFromString(e,"text/xml"),t&&t.documentElement&&t.documentElement.nodeName!="parsererror"?t:null},D=e.parseJSON||function(e){return window.eval("("+e+")")},P=function(t,n,r){var i=t.getResponseHeader("content-type")||"",s=n==="xml"||!n&&i.indexOf("xml")>=0,o=s?t.responseXML:t.responseText;return s&&o.documentElement.nodeName==="parsererror"&&e.error&&e.error("parsererror"),r&&r.dataFilter&&(o=r.dataFilter(o,n)),typeof o=="string"&&(n==="json"||!n&&i.indexOf("json")>=0?o=D(o):(n==="script"||!n&&i.indexOf("javascript")>=0)&&e.globalEval(o)),o}}if(!this.length)return i("ajaxSubmit: skipping submit process - no element selected"),this;var r,s,o,u=this;typeof n=="function"&&(n={success:n}),r=this.attr("method"),s=this.attr("action"),o=typeof s=="string"?e.trim(s):"",o=o||window.location.href||"",o&&(o=(o.match(/^([^#]+)/)||[])[1]),n=e.extend(!0,{url:o,success:e.ajaxSettings.success,type:r||"GET",iframeSrc:/^https/i.test(window.location.href||"")?"javascript:false":"about:blank"},n);var a={};this.trigger("form-pre-serialize",[this,n,a]);if(a.veto)return i("ajaxSubmit: submit vetoed via form-pre-serialize trigger"),this;if(n.beforeSerialize&&n.beforeSerialize(this,n)===!1)return i("ajaxSubmit: submit aborted via beforeSerialize callback"),this;var f=n.traditional;f===undefined&&(f=e.ajaxSettings.traditional);var l=[],c,h=this.formToArray(n.semantic,l);n.data&&(n.extraData=n.data,c=e.param(n.data,f));if(n.beforeSubmit&&n.beforeSubmit(h,this,n)===!1)return i("ajaxSubmit: submit aborted via beforeSubmit callback"),this;this.trigger("form-submit-validate",[h,this,n,a]);if(a.veto)return i("ajaxSubmit: submit vetoed via form-submit-validate trigger"),this;var p=e.param(h,f);c&&(p=p?p+"&"+c:c),n.type.toUpperCase()=="GET"?(n.url+=(n.url.indexOf("?")>=0?"&":"?")+p,n.data=null):n.data=p;var d=[];n.resetForm&&d.push(function(){u.resetForm()}),n.clearForm&&d.push(function(){u.clearForm(n.includeHidden)});if(!n.dataType&&n.target){var v=n.success||function(){};d.push(function(t){var r=n.replaceTarget?"replaceWith":"html";e(n.target)[r](t).each(v,arguments)})}else n.success&&d.push(n.success);n.success=function(e,t,r){var i=n.context||n;for(var s=0,o=d.length;s<o;s++)d[s].apply(i,[e,t,r||u,u])};var m=e("input:file:enabled[value]",this),g=m.length>0,y="multipart/form-data",b=u.attr("enctype")==y||u.attr("encoding")==y,w=t.fileapi&&t.formdata;i("fileAPI :"+w);var E=(g||b)&&!w;n.iframe!==!1&&(n.iframe||E)?n.closeKeepAlive?e.get(n.closeKeepAlive,function(){T(h)}):T(h):(g||b)&&w?x(h):e.ajax(n);for(var S=0;S<l.length;S++)l[S]=null;return this.trigger("form-submit-notify",[this,n]),this},e.fn.ajaxForm=function(t){t=t||{},t.delegation=t.delegation&&e.isFunction(e.fn.on);if(!t.delegation&&this.length===0){var s={s:this.selector,c:this.context};return!e.isReady&&s.s?(i("DOM not ready, queuing ajaxForm"),e(function(){e(s.s,s.c).ajaxForm(t)}),this):(i("terminating; zero elements found by selector"+(e.isReady?"":" (DOM not ready)")),this)}return t.delegation?(e(document).off("submit.form-plugin",this.selector,n).off("click.form-plugin",this.selector,r).on("submit.form-plugin",this.selector,t,n).on("click.form-plugin",this.selector,t,r),this):this.ajaxFormUnbind().bind("submit.form-plugin",t,n).bind("click.form-plugin",t,r)},e.fn.ajaxFormUnbind=function(){return this.unbind("submit.form-plugin click.form-plugin")},e.fn.formToArray=function(n,r){var i=[];if(this.length===0)return i;var s=this[0],o=n?s.getElementsByTagName("*"):s.elements;if(!o)return i;var u,a,f,l,c,h,p;for(u=0,h=o.length;u<h;u++){c=o[u],f=c.name;if(!f)continue;if(n&&s.clk&&c.type=="image"){!c.disabled&&s.clk==c&&(i.push({name:f,value:e(c).val(),type:c.type}),i.push({name:f+".x",value:s.clk_x},{name:f+".y",value:s.clk_y}));continue}l=e.fieldValue(c,!0);if(l&&l.constructor==Array){r&&r.push(c);for(a=0,p=l.length;a<p;a++)i.push({name:f,value:l[a]})}else if(t.fileapi&&c.type=="file"&&!c.disabled){r&&r.push(c);var d=c.files;if(d.length)for(a=0;a<d.length;a++)i.push({name:f,value:d[a],type:c.type});else i.push({name:f,value:"",type:c.type})}else l!==null&&typeof l!="undefined"&&(r&&r.push(c),i.push({name:f,value:l,type:c.type,required:c.required}))}if(!n&&s.clk){var v=e(s.clk),m=v[0];f=m.name,f&&!m.disabled&&m.type=="image"&&(i.push({name:f,value:v.val()}),i.push({name:f+".x",value:s.clk_x},{name:f+".y",value:s.clk_y}))}return i},e.fn.formSerialize=function(t){return e.param(this.formToArray(t))},e.fn.fieldSerialize=function(t){var n=[];return this.each(function(){var r=this.name;if(!r)return;var i=e.fieldValue(this,t);if(i&&i.constructor==Array)for(var s=0,o=i.length;s<o;s++)n.push({name:r,value:i[s]});else i!==null&&typeof i!="undefined"&&n.push({name:this.name,value:i})}),e.param(n)},e.fn.fieldValue=function(t){for(var n=[],r=0,i=this.length;r<i;r++){var s=this[r],o=e.fieldValue(s,t);if(o===null||typeof o=="undefined"||o.constructor==Array&&!o.length)continue;o.constructor==Array?e.merge(n,o):n.push(o)}return n},e.fieldValue=function(t,n){var r=t.name,i=t.type,s=t.tagName.toLowerCase();n===undefined&&(n=!0);if(n&&(!r||t.disabled||i=="reset"||i=="button"||(i=="checkbox"||i=="radio")&&!t.checked||(i=="submit"||i=="image")&&t.form&&t.form.clk!=t||s=="select"&&t.selectedIndex==-1))return null;if(s=="select"){var o=t.selectedIndex;if(o<0)return null;var u=[],a=t.options,f=i=="select-one",l=f?o+1:a.length;for(var c=f?o:0;c<l;c++){var h=a[c];if(h.selected){var p=h.value;p||(p=h.attributes&&h.attributes.value&&!h.attributes.value.specified?h.text:h.value);if(f)return p;u.push(p)}}return u}return e(t).val()},e.fn.clearForm=function(t){return this.each(function(){e("input,select,textarea",this).clearFields(t)})},e.fn.clearFields=e.fn.clearInputs=function(t){var n=/^(?:color|date|datetime|email|month|number|password|range|search|tel|text|time|url|week)$/i;return this.each(function(){var r=this.type,i=this.tagName.toLowerCase();n.test(r)||i=="textarea"?this.value="":r=="checkbox"||r=="radio"?this.checked=!1:i=="select"?this.selectedIndex=-1:t&&(t===!0&&/hidden/.test(r)||typeof t=="string"&&e(this).is(t))&&(this.value="")})},e.fn.resetForm=function(){return this.each(function(){(typeof this.reset=="function"||typeof this.reset=="object"&&!this.reset.nodeType)&&this.reset()})},e.fn.enable=function(e){return e===undefined&&(e=!0),this.each(function(){this.disabled=!e})},e.fn.selected=function(t){return t===undefined&&(t=!0),this.each(function(){var n=this.type;if(n=="checkbox"||n=="radio")this.checked=t;else if(this.tagName.toLowerCase()=="option"){var r=e(this).parent("select");t&&r[0]&&r[0].type=="select-one"&&r.find("option").selected(!1),this.selected=t}})},e.fn.ajaxSubmit.debug=!1})(jQuery),jQuery.cookie=function(e,t,n){if(arguments.length>1&&(t===null||typeof t!="object")){n=jQuery.extend({},n),t===null&&(n.expires=-1);if(typeof n.expires=="number"){var r=n.expires,i=n.expires=new Date;i.setDate(i.getDate()+r)}return document.cookie=[encodeURIComponent(e),"=",n.raw?String(t):encodeURIComponent(String(t)),n.expires?"; expires="+n.expires.toUTCString():"",n.path?"; path="+n.path:"",n.domain?"; domain="+n.domain:"",n.secure?"; secure":""].join("")}n=t||{};var s,o=n.raw?function(e){return e}:decodeURIComponent;return(s=(new RegExp("(?:^|; )"+encodeURIComponent(e)+"=([^;]*)")).exec(document.cookie))?o(s[1]):null},exports={},function(e){"use strict";e.logging=function(){var t={},n={loggers:{},mapping:{},names:{},format_error:function(e,t){return t!==undefined&&(e+="- File "+t.fileName+" - Line "+t.lineNumber+": "+t),e},debug:10,info:20,warn:30,error:40,critical:50,logclass:"log"};return n.levels={debug:{level:n.debug,name:"DEBUG"},info:{level:n.info,name:"INFO"},warn:{level:n.warn,name:"WARN"},error:{level:n.error,name:"ERROR",f:function(e,t){return n.format_error(e,t)}},critical:{level:n.critical,name:"CRITICAL",f:function(e,t){return n.format_error(e,t)}}},e.each(n.levels,function(e,n){t[n.level]=n}),n.getLevelName=function(e){var n=t[e];return n!==undefined?n=n.name:n="Level-"+e,n},n.default_formatter=function(e,t){var r=n.getLevelName(t),i=new Date,s=i.getHours(),o=i.getMinutes(),u=i.getSeconds();return s<10&&(s="0"+s),o<10&&(o="0"+o),u<10&&(u="0"+u),s+":"+o+":"+u+" - "+r+" - "+e},n.html_formatter=function(e,t){var r=n.getLevelName(t);return e=n.default_formatter(e,t),'<pre class="'+n.logclass+" "+r.toLowerCase()+'">'+e+"</pre>"},n.getLogger=function(t){var r="log",i=10,s=[],o;return t===undefined&&(t="root"),o=n.loggers[t],o!==undefined?o:(o={name:t,level:function(){return i},set_level:function(e){i=parseInt(String(e),10)},addHandler:function(e){e!==undefined&&(e.formatter===undefined&&(e={formatter:n.default_formatter,log:e}),s.push(e))},log:function(t,n){if(n<i)return;e.each(s,function(e,r){r.log(r.formatter(t,n))})}},console!==undefined&&console.log!==undefined&&o.addHandler(function(e){console.log(e)}),e.each(n.levels,function(e,t){o[e]=function(e,n){t.f&&(e=t.f(e,n)),o.log(e,t.level)}}),n.loggers[o.name]=o,o)},n}(),e.djpcms={widgets:{},base_widget:{_create:function(){return this},factory:function(){return e.djpcms.widgets[this.name]},destroy:function(){var e=this.factory().instances,t=e.indexOf(this.id),n;return t!==-1&&(n=e[t],delete e[t],delete n.element[0].djpcms_widget),n},ui:function(t,n,r){return e.djpcms.ui[t](n,r)},tostring:function(e){return e?e=this.name+" "+this.id+" - "+e:e=this.name+" "+this.id,e},debug:function(t){e.djpcms.logger.debug(this.tostring(t))},info:function(t){e.djpcms.logger.info(this.tostring(t))},warn:function(t){e.djpcms.logger.warn(this.tostring(t))},error:function(t){e.djpcms.logger.error(this.tostring(t))},critical:function(t){e.djpcms.logger.critical(this.tostring(t))}},widgetmaker:{name:"widget",defaultElement:"<div>",selector:null,instance:function(e){return typeof e!="number"&&(e=e.id),this.instances[e]},options:function(){return e.djpcms.options[this.name]},create:function(t,n){var r=this,i=t.data("options")||t.data(),s,o;return s=e.extend({},r.factory),s.id=parseInt(r.instances.push(s),10)-1,s.element=t,t[0].djpcms_widget=s,i&&(n=e.extend(!0,{},n,i)),s.config=n,e.djpcms.logger.debug("Creating widget "+s.name),s._create(),r.instance(s.id)},make:function(t,n){var r=this,i=[],s;return n=e.extend(!0,{},r.options(),n),e.each(t,function(){s=r.create(e(this),n),s!==undefined&&i.push(s)}),i.length===1&&(i=i[0]),i},decorate:function(t){var n=this.selector;n&&(t.is(n)&&this.make(t),this.make(e(n,t)))},ui:function(t,n){var r=t;return n===undefined&&e.isPlainObject(t)&&(n=t,r=undefined),r=e(r||this.defaultElement),this.make(r,n)},create_ui:function(){var e=this;return function(t,n){return e.ui(t,n)}}},ui:{name:"djpcms",widget_head:"ui-widget-header",widget_body:"ui-widget-content",corner_top:"ui-corner-top",corner_bottom:"ui-corner-bottom",ui_input:"ui-input",dialog:function(t,n){var r=e.djpcms.ui,i=!0,s;return n=n||{},n.autoOpen===!1&&(i=!1),n.autoOpen=!1,s=t.dialog(n).dialog("widget"),r.icons==="fontawesome"&&e(".ui-dialog-titlebar-close",s).html('<i class="icon-remove"></i>').addClass(r.classes.float_right),i&&t.dialog("open"),t}}},e.djpcms=function(t){function f(n,r){var i=r||t.widgetmaker,s=i.factory||t.base_widget;return n.factory=e.extend({},s,n),n.superClass=r,n.instances=[],e.each(i,function(e,t){n[e]===undefined&&(n[e]=t)}),n}function l(n){var r=n.name||t.widgetmaker.name,i=t.widgets[r]||t.widgets[t.widgetmaker.name],s=n.config;n.name=r,s!==undefined&&delete n.config,a[r]&&(s=e.extend(!0,a[r],s)),a[r]=s,n=f(n,i),t.widgets[r]=n,t.ui[r]=n.create_ui()}function c(t){t=e(t),t.length&&u.addHandler({formatter:e.logging.html_formatter,log:function(e){t.prepend(e)}})}function h(t,n){var r={xhr:t};return n&&(r=e.extend(r,n)),r}function p(t){e.data(document,"djpcms")?t():o.push(t)}function d(t){e.extend(!0,a,t)}function v(e){r[e.id]=e}function m(t){e.djpcms.widgets.hasOwnMethod(t)&&delete e.djpcms.widgets[t]}function g(e,t){var n=e.header,i=r[n];return i?i=i.handle(e.body,t,a)&&e.error:u.error("Could not find callback "+n),i}function y(e,t){var r=n[e];return r?t&&(r.action=t):(r={action:t,ids:{}},n[e]=r),r}function b(e,t){var n=y(e,null);n.ids[t]=t}function w(e,t){var n=y(e,null);if(n.ids[t])return delete n.ids[t],n.action}function E(e,t,n){var r=!1;return t==="success"&&(r=g(e,n)),i=!1,r}function S(t){return t.each(function(){var t=e(this),n=a,r=e(".djp-logging-panel",t),i=[];i.length||(this===document&&(t=e("body")),t.addClass("djpcms-loaded").trigger("djpcms-before-loading"),r&&c(r),e.each(e.djpcms.widgets,function(e,n){n.decorate(t)}),this===document&&(e.data(this,"djpcms",n),e.each(o,function(e,t){t()}),o=[]),t.trigger("djpcms-after-loading"))})}var n={},r={},i=!1,s=null,o=[],u=e.logging.getLogger(),a={media_url:"/media/",debug:!1,remove_effect:{type:"drop",duration:500},fadetime:200};return e.extend(t,{construct:S,options:a,jsonParse:g,addJsonCallBack:v,jsonCallBack:E,decorator:l,set_options:d,ajaxparams:h,set_inrequest:function(e){i=e},before_form_submit:[],addAction:y,registerActionElement:b,getAction:w,inrequest:function(){return i},logger:u,queue:p,panel:function(){return s||(s=e("<div>").hide().appendTo(e("body")).addClass("float-panel ui-widget ui-widget-content ui-corner-all").css({position:"absolute","text-align":"left",padding:"5px"})),s},smartwidth:function(e){return Math.max(15*Math.sqrt(e.length),200)}})}(e.djpcms),e.djpcms.decorator({config:{classes:{widget:"ui-widget",head:"ui-widget-header",body:"ui-widget-content",foot:"ui-widget-footer",active:"ui-state-active",clickable:"ui-clickable",float_right:"f-right"}}}),e.djpcms.confirmation_dialog=function(t,n,r,i){var s=e('<div title="'+t+'"></div>').html(String(n)),o=e.extend({},i,{modal:!0,draggable:!1,resizable:!1,buttons:{Ok:function(){e(this).dialog("close"),r(!0)},Cancel:function(){e(this).dialog("close"),r(!1)}},close:function(e,t){s.dialog("destroy").remove()}});return e.djpcms.ui.dialog(s,o)},e.djpcms.warning_dialog=function(t,n,r){var i={dialogClass:"ui-state-error",autoOpen:!1},s=e.djpcms.confirmation_dialog(t,n,r,i);return e(".ui-dialog-titlebar, .ui-dialog-buttonpane",s.dialog("widget")).addClass("ui-state-error"),s.dialog("open"),s},e.djpcms.ajax_loader=function(n,r,i,s,o){var u=function(t){var a=this;o&&!t?e("<div></div>").html(o).dialog({modal:!0,draggable:!1,resizable:!1,buttons:{Ok:function(){e(this).dialog("close"),u(!0)},Cancel:function(){e(this).dialog("close"),e.djpcms.set_inrequest(!1)}}}):e.ajax({url:n,type:i||"post",dataType:"json",success:function(t,n){e.djpcms.set_inrequest(!1),e.djpcms.jsonCallBack(t,n,a)},data:e.djpcms.ajaxparams(r,s)})};return u},e.djpcms.ajax_loader_from_tool=function(t){if(t.ajax)return e.djpcms.ajax_loader(t.url,t.action,t.method,t.data,t.conf)},e.djpcms.errorDialog=function(t,n){n=n||"Something did not work";var r=e('<div title="'+n+'"></div>').html(String(t)),i=e.djpcms.smartwidth(t);r.dialog({modal:!0,autoOpen:!1,dialogClass:"ui-state-error",width:i}),e(".ui-dialog-titlebar",r.dialog("widget")).addClass("ui-state-error"),r.dialog("open")},e.djpcms.addJsonCallBack({id:"error",handle:function(t,n){e.djpcms.errorDialog(t)}}),e.djpcms.addJsonCallBack({id:"servererror",handle:function(t,n){e.djpcms.errorDialog(t,"Unhandled Server Error")}}),e.djpcms.addJsonCallBack({id:"message",handle:function(t,n){return e.djpcms.logger.info(t),!0}}),e.djpcms.addJsonCallBack({id:"empty",handle:function(e,t){return!0}}),e.djpcms.addJsonCallBack({id:"collection",handle:function(t,n){return e.each(t,function(t,r){e.djpcms.jsonParse(r,n)}),!0}}),e.djpcms.addJsonCallBack({id:"htmls",handle:function(t,n,r){return e.each(t,function(t,i){var s=e(i.identifier,n),o=r.fadetime,u;!s.length&&i.alldocument&&(s=e(i.identifier)),s.length&&(i.type==="hide"?s.hide():i.type==="show"?s.show():i.type==="value"?s.val(i.html):i.type==="append"?e(i.html).djpcms().appendTo(s):(u=e(i.html).djpcms(),s.show(),s.fadeOut(o,"linear",function(){if(i.type==="replacewith")s.replaceWith(u);else if(i.type==="addto")s.append(u);else{var t=e("<div></div>");s.empty().append(t),t.replaceWith(u)}s.fadeIn(o)})))}),!0}}),e.djpcms.addJsonCallBack({id:"attribute",handle:function(t,n){var r=[];e.each(t,function(t,r){var i;r.alldocument?i=e(r.selector):i=e(r.selector,n),i.length&&(r.elem=i)}),e.each(t,function(e,t){t.elem&&t.elem.attr(t.attr,t.value)})}}),e.djpcms.addJsonCallBack({id:"remove",handle:function(t,n){return e.each(t,function(t,r){var i=e(r.identifier,n),s=e.djpcms.options.remove_effect;!i.length&&r.alldocument&&(i=e(r.identifier)),i.length&&i.fadeIn(s.duration,function(){i.remove()})}),!0}}),e.djpcms.addJsonCallBack({id:"redirect",handle:function(e,t){window.location=e}}),e.djpcms.addJsonCallBack({id:"dialog",handle:function(t,n){var r=e("<div></div>").html(t.html).djpcms(),i={},s=t.options;return e.each(t.buttons,function(t,n){i[n.name]=function(){n.d=e(this),n.dialogcallBack=function(t){e.djpcms.jsonCallBack(t,"success",r),n.close&&n.d.dialog("close")};if(n.url){var t=e("form",r).formToArray(),i;n.func&&(i=e.djpcms.ajaxparams(n.func),e.each(i,function(e,n){t.push({name:e,value:n})})),e.post(n.url,e.param(t),n.dialogcallBack,"json")}else n.d.dialog("close")}}),s.buttons=i,r.dialog(s),!0}}),e.djpcms.format_currency=function(e,t){t||(t=3),e=e.replace(/, /g,"");var n=parseFloat(e),r=!1,i=!1,s="",o,u,a,f,l,c,h,p;if(isNaN(n))u=e;else{u=e.split(".",2),n<0&&(r=!0,n=Math.abs(n)),a=parseInt(n,10),u.length===2&&(s=u[1],s?(i=!0,s=n-a):s=".");if(i){h=Math.pow(10,t),p=String(parseInt(n*h,10)/h).split(".")[1],s="",i=!1;for(o=0;o<Math.min(p.length,t);o++)s+=p[o],parseInt(p[o],10)>0&&(i=!0);i&&(s="."+s)}a+="",c=a.length,u="";for(o=0;o<c;o++)u+=a[o],l=c-o-1,f=parseInt(l/3,10),3*f===l&&l>0&&(u+=",");u+=s,r?u="-"+u:u=String(u)}return{value:u,negative:r}},e.djpcms.decorator({name:"ajax",description:"add ajax functionality to links, buttons, selects and forms",defaultElement:"<a>",selector:"a.ajax, button.ajax, select.ajax, form.ajax, input.ajax",config:{dataType:"json",classes:{submit:"submitted",autoload:"autoload"},confirm_actions:{"delete":"Please confirm delete",flush:"Please confirm flush"},effect:{name:"fade",options:{},speed:50},form:{iframe:!1,beforeSerialize:function(e,t){return!0},beforeSubmit:function(t,n,r){var i=n[0].djpcms_widget,s=!i.disabled;return s&&(i.disabled=!0,e.each(e.djpcms.before_form_submit,function(){t=this(t,n)}),n.addClass(i.config.classes.submit)),s},success:function(e,t,n,r){var i=r[0].djpcms_widget;return i.finished(e,t,n)},error:function(e,t,n,r){var i=r[0].djpcms_widget;return i.finished(e,t,n)}},timeout:30},_create:function(){var e=this,t=e.element;e.disabled=!1,t.is("select")?(e.type="select",e.create_select()):t.is("input")?(e.type="input",e.create_select()):t.is("form")?(e.type="form",e.create_form()):(e.type="link",e.create_link())},finished:function(t,n,r){var i=this,s=i.element,o=i.config.effect,u=e(".form-messages, .error",s),a=0;s.removeClass(i.config.classes.submit),i.disabled=!1,u.hide(o.name,o.options,o.speed,function(){a+=1,e(this).html("").show(),a===u.length&&e.djpcms.jsonCallBack(t,n,s)})},form_data:function(){var e=this.element,t=e.closest("form"),n={conf:e.data("warning"),name:e.attr("name"),url:e.attr("href")||e.data("href"),type:e.data("method")||"get",submit:e.data("submit")};return t.length===1&&(n.form=t),!n.url&&n.form&&(n.url=n.form.attr("action")),n.url||(n.url=window.location.toString()),n},submit:function(t){function r(r){if(r){var i=e.djpcms.ajaxparams(t.name,t.submit),s={url:t.url,type:t.type,dataType:n.config.dataType,data:i};n.info("Submitting ajax "+s.type+' request "'+t.name+'"'),t.form?(e.extend(s,n.config.form),t.form.ajaxSubmit(s)):(s.data.value=n.element.val(),s.success=e.djpcms.jsonCallBack,e.ajax(s))}}var n=this;t.conf?e.djpcms.warning_dialog(t.conf.title||"",t.conf.body||t.conf,r):r(!0)},create_select:function(){var e=this,t=e.form_data();e.element.change(function(n){e.submit(t)})},create_link:function(){var e=this,t=e.form_data();e.element.click(function(n){n.preventDefault(),e.submit(t)})},create_form:function(){var t=this,n=t.element,r={url:n.attr("action"),type:n.attr("method"),dataType:t.config.dataType},i;e.extend(r,t.config.form),n.ajaxForm(r),n.hasClass(t.config.classes.autoload)&&(i=n.attr("name"),n[0].clk=e(":submit[name='"+i+"']",n)[0],n.submit())}}),e.djpcms.decorator({name:"autocomplete",defaultElement:"<input>",selector:"input.autocomplete",config:{classes:{autocomplete:"autocomplete",list:"multiSelectList",container:"multiSelectContainer"},removelink:function(t){return e('<a href="#"><i class="icon-remove"></i></a>')},minLength:2,maxRows:50,search_string:"q",separator:", ",multiple:!1},split:function(e){return e.split(/,\s*/)},add_data:function(e){var t=this;return t.config.multiple?t.addOption(e):(t.real.val(e.real_value),t.element.val(e.value)),!1},get_autocomplete_data:function(e,t,n){var r=this.element.val();this.multiple||this.real.data("value")!==r&&this.real.val(r)},addOption:function(t){var n=this,r=n.list,i=r.data("selections"),s=n.config,o=e("<li>"),u=e("<option>",{text:t.label,val:t.real_value}),a=u.val();i.indexOf(a)===-1&&(n.real.append(u),i.push(a),o.append(e("<span>",{html:t.label})).append(s.removelink(n)).data("option",u).appendTo(n.list),n.list.children().length&&n.list_container.show(),u.prop("selected",!0),n.element.val(""))},dropListItem:function(e){var t=e.data("option"),n=this.list.data("selections"),r;e.remove(),this.list.children().length===0&&this.list_container.hide(),r=n.indexOf(t.val()),r!==-1&&n.splice(r,1),t.remove()},buildDom:function(){var t=this,n=t.config,r=e.djpcms.options.input.classes,i=e("<div>",{"class":n.classes.container}),s=t.list;t.wrapper&&(t.wrapper.after(i),i.addClass(r.control).prepend(t.wrapper.removeClass(r.control)),s=e("<div>",{"class":r.input}).addClass(n.classes.container).append(t.list)),t.list_container=s.hide(),i.append(t.list_container)},_create:function(){var t=this,n=t.config,r=this.element,i=r.attr("name"),s=i.length;n.select=function(e,n){return t.add_data(n.item)},t.wrapper=r.parent("."+e.djpcms.options.input.classes.input),t.wrapper.length||(t.wrapper=null),n.position={of:t.wrapper||r},n.multiple?(i.substring(s-2,s)==="[]"&&(i=i.substring(0,s-2)),t.real=e('<select name="'+i+'[]" multiple="multiple"></select>'),t.list=e("<ul>").data("selections",[]).addClass(n.classes.list),t.buildDom(),t.list.delegate("a","click",function(n){return n.preventDefault(),t.dropListItem(e(this).closest("li")),!1}),n.focus=function(){return!1},r.bind("keydown",function(t){t.keyCode===e.ui.keyCode.TAB&&e(this).data("autocomplete").menu.active&&t.preventDefault()})):t.real=e('<input name="'+i+'"></input>'),r.attr("name",i+"_proxy").before(t.real.hide()),n.initials_value&&e.each(n.initials_value,function(e,n){t.add_data({real_value:n[0],value:n[1]})});if(n.choices&&n.choices.length){var o=[];e.each(n.choices,function(e,t){o[e]={value:t[0],label:t[1]}}),n.source=function(e,t){if(n.multiple)throw"Not implemented";return o},r.autocomplete(n)}else n.url?(n.source=function(t,r){var i={style:"full",maxRows:n.maxRows,search_string:n.search_string},s;i[n.search_string]=t.term,s=e.djpcms.ajax_loader(n.url,"autocomplete","get",i),e.proxy(s,r)()},r.autocomplete(n)):t.warn("Could not find choices or url for autocomplete data")}}),e.djpcms.addJsonCallBack({id:"autocomplete",handle:function(t,n){n(e.map(t,function(e){return{value:e[0],label:e[1],real_value:e[2]}}))}}),e.djpcms.decorator({name:"readonly",defaultElement:"<select>",selector:"select.readonly",_create:function(){var t=this.element,n=e(":selected",t);t.change(function(){t.children().prop("selected",!1),n.prop("selected",!0)})}}),e.djpcms.decorator({name:"input",defaultElement:'<input type="text">',selector:".ui-input",config:{submit:!1,classes:{input:"ui-input",control:"control",focus:"focus"}},_create:function(){var t=this,n=t.element,r=t.config,i;n.is("input")||n.is("textarea")?(n.removeClass(r.classes.input),t.wrapper=e("<div></div>").addClass(r.classes.input),i=n.prev(),i.length?i.after(t.wrapper):(i=n.parent(),i.length&&i.prepend(t.wrapper)),t.wrapper.append(n).addClass(n.attr("name"))):(t.wrapper=n,n=t.wrapper.children("input,textarea"),n.length===1&&(e.extend(!0,r,n.data("options")),t.element=n)),t.element.focus(function(){t.wrapper.addClass(r.classes.focus)}).blur(function(){t.wrapper.removeClass(r.classes.focus)}),r.submit&&t.element.keypress(function(e){if(e.which===13){var t=n.closest("form");t.length&&t.submit()}})}}),e.djpcms.decorator({name:"icon",defaultElement:"i",sources:{fontawesome:function(e,t){t?t.substring(0,5)!=="icon-"&&(t="icon-"+t):t="icon-question-sign",e.element.prepend('<i class="'+t+'"></i>')}},config:{source:"fontawesome"},_create:function(){var t=this.config,n=this.sources[t.source],r=t.icon;n&&(e.isPlainObject(r)&&(r=r[t.source]),n(this,r))}}),e.djpcms.decorator({name:"button",defaultElement:"<button>",description:"Add button like functionalities to html objects. It can handle anchors, buttons, inputs and checkboxes",selector:".btn",config:{disabled:null,text:!0,icon:null,classes:{button:"btn",button_small:"btn-small",button_large:"btn-large",button_group:"btn-group"}},_create:function(){var e=this,t=e.element.hide(),n=e.config,r=n.classes,i,s,o,u,a;t.is("[type=checkbox]")?e.type="checkbox":t.is("[type=radio]")?e.type="radio":t.is("input")?e.type="input":e.type="button",e.type==="checkbox"||e.type==="radio"?(u=!0,s="label[for='"+t.attr("id")+"']",o=t.parents().last(),i=o.find(s),i&&(t.removeClass(r.button),i.attr("title",i.html()))):i=t,i?(e.buttonElement=i,a=i.children(),n.text?n.text!==!0&&i.html(n.text):i.html(""),n.icon&&e.ui("icon",i,{icon:n.icon}),i.addClass(r.button).css("display","inline-block"),u&&(e.refresh(),t.bind("change",function(){e.refresh()}))):e.destroy()},refresh:function(){var t=this,n=e.djpcms.options.widget.classes;t.element.prop("checked")?(e.djpcms.logger.debug("checked"),t.buttonElement.addClass(n.active)):(e.djpcms.logger.debug("unchecked"),t.buttonElement.removeClass(n.active))}}),e.djpcms.decorator({name:"alert",selector:".alert",config:{dismiss:!0,icon:{fontawesome:"remove"},effect:{name:"fade",options:{},speed:400},"float":"right"},_create:function(){var t=this,n=t.config,r=n.effect,i=e("<a href='#'>").css({"float":n.float}).click(function(n){n.preventDefault(),t.element.hide(r.name,r.options,r.speed,function(){e(this).remove()})});e.djpcms.ui.icon(i,n),t.element.append(i)}}),e.djpcms.decorator({name:"collapsable",description:"Decorate box elements",selector:"a.collapse",config:{classes:{collapsable:"bd"},effect:{type:"blind",options:{},duration:10},icons:{open:{fontawesome:"plus-sign"},close:{fontawesome:"minus-sign"}}},_create:function(){var t=this,n=e.djpcms.options.widget.classes;t.widget=t.element.closest("."+n.widget),t.body=t.widget.find("."+t.config.classes.collapsable).first(),t.body.length&&(t.toggle(),t.element.mousedown(function(e){e.stopPropagation()}).click(function(){return t.widget.toggleClass("collapsed"),t.toggle(),!1}))},toggle:function(){var t=this,n=t.config.effect,r=t.config.icons,i=t.element.html("");t.widget.hasClass("collapsed")?(t.body.hide(n.type,n.options,n.duration,function(){e.djpcms.ui.icon(i,{icon:r.open})}),t.info("closed body")):(t.body.show(n.type,n.options,n.duration,function(){e.djpcms.ui.icon(i,{icon:r.close})}),t.info("opened body"))}}),e.djpcms.decorator({name:"autocomplete_off",decorate:function(t){e(".autocomplete-off",t).each(function(){e(this).attr("autocomplete","off")}),e("input:password",t).each(function(){e(this).attr("autocomplete","off")})}}),e.djpcms.decorator({name:"datepicker",selector:"input.dateinput",config:{dateFormat:"d M yy"},_create:function(){this.element.datepicker(this.config)}}),e.djpcms.decorator({name:"numeric",selector:"input.numeric",config:{classes:{negative:"negative"}},format:function(){var t=this.element,n=this.config.classes.negative,r=e.djpcms.format_currency(t.val());r.negative?t.addClass(n):t.removeClass(n),t.val(r.value)},_create:function(){var e=this;this.element.keyup(function(){e.format()})}}),e.djpcms.decorator({name:"showdown",selector:".markdown",_create:function(){var e=this.config.markdown,t;e&&Showdown&&(t=new Showdown.converter,e=t.makeHtml(e)),this.element.html(e)}}),e.fn.commonAncestor=function(){if(!this.length)return e([]);var t=[],n=Infinity,r,i,s,o;this.each(function(){var r=e(this).parents();t.push(r),n=Math.min(n,r.length)}),e.each(t,function(e,r){t[e]=r.slice(r.length-n)});for(r=0;r<t[0].length;r++){s=t[0][r],o=!0;for(i=1;i<t.length;i++)if(t[i][r]!==s){o=!1;break}if(o)return e(s)}return e([])},e.fn.extend({djpcms:function(){return e.djpcms.construct(this)}})}(jQuery);