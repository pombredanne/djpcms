/*
 * jQuery.splitter.js - A two-pane splitter plugin
 *
 *   
 */
/*global jQuery*/
(function($){

    $.splitter = (function() {
        var defaults = {
                logger: null,
                cookie: false,          // requires $.cookie plugin
                type: 'v',
                activeClass: 'active',  // class name for active splitter
                pxPerKey: 8,            // splitter px moved per keypress
                tabIndex: 0,            // tab order indicator
                accessKey: '',          // accessKey for splitbar
                outline: true
            },
            splitters = {
                v: {                    // Vertical splitters:
                    keyLeft: 39, keyRight: 37, cursor: "e-resize",
                    splitbarClass: "vsplitbar", outlineClass: "voutline",
                    type: 'v', eventPos: "pageX", origin: "left",
                    split: "width",  pxSplit: "offsetWidth",  side1: "Left", side2: "Right",
                    fixed: "height", pxFixed: "offsetHeight", side3: "Top",  side4: "Bottom",
                    name: 'vertical'
                },
                h: {                    // Horizontal splitters:
                    keyTop: 40, keyBottom: 38,  cursor: "n-resize",
                    splitbarClass: "hsplitbar", outlineClass: "houtline",
                    type: 'h', eventPos: "pageY", origin: "top",
                    split: "height", pxSplit: "offsetHeight", side1: "Top",  side2: "Bottom",
                    fixed: "width",  pxFixed: "offsetWidth",  side3: "Left", side4: "Right",
                    name: 'horizontal'
                }
            },
            csspanels = {
                position: "absolute",           // positioned inside splitter container
                "z-index": "1",                 // splitbar is positioned above
                "-moz-outline-style": "none"    // don't show dotted outline
            };
        
        function bar_position(evt) {
            var dims = this.dims;
            if(dims.barpos === null) {
                dims.barpos = this.panes[0].el[0][this.options.pxSplit] - evt[this.options.eventPos];
            } else {
                return dims.barpos + evt[this.options.eventPos];
            }
        }
        
        function startMove(evt) {
            this.dims.barpos = null;
            this.barpos(evt);
            if(this.options.logger) {
                this.options.logger.info('Start moving splitter');
            }
            this.bar.addClass(this.options.activeClass);
            $(document).bind("mousemove", this.Move)
                       .bind("mouseup", this.endMove);
        }
        
        function Move(evt) {
            this.elems.css("-webkit-user-select", "none");
            this.split(this.barpos(evt));
        }
        
        function endMove(evt) {
            this.split(this.barpos(evt));
            this.bar.removeClass(this.options.activeClass);
            this.elems.css("-webkit-user-select", "text");   // let Safari select text again
            $(document).unbind("mousemove", this.Move)
                       .unbind("mouseup", this.endMove);
            if(this.options.logger) {
                this.options.logger.info('End moving splitter');
            }
        }
        
        function dimSum(jq, dims) {
            // Opera returns -1 for missing min/max width, turn into 0
            var sum = 0, i;
            for ( i=1; i < arguments.length; i++ ) {
                sum += Math.max(parseInt(jq.css(arguments[i])) || 0, 0);
            }
            return sum;
        }
        
        function resplit(newPos) {
            var dims  = this.dims,
                opts  = this.options,
                panes =  this.panes,
                A = panes[0],
                B = panes[1];
            // Constrain new splitbar position to fit pane size limits
            newPos = Math.max(A.min, dims.net_size - B.max, 
                              Math.min(newPos, A.max, dims.net_size - dims.bar - B.min));
            // Resize/position the two panes
            dims.bar = this.bar[0][opts.pxSplit];     // bar size may change during dock
            this.bar.css(opts.origin, newPos)
                .css(opts.fixed, dims.net_size2);
            A.el.css(opts.origin, 0)
                .css(opts.split, newPos)
                .css(opts.fixed, dims.net_size2).trigger("resize");
            B.el.css(opts.origin, newPos + dims.bar)
                .css(opts.split, dims.net_size - dims.bar - newPos)
                .css(opts.fixed, dims.net_size2);
            // IE fires resize for us; all others pay cash
            if(!$.browser.msie ) {
                A.el.trigger("resize");
                B.el.trigger("resize");
            }
        }
        
        function splitterResize(e, size){
            var splitter = this.container[0],
                dims = this.dims,
                opts = this.options;
            if ( e.target !== splitter ) { return; }
            // Determine new width/height of splitter container
            dims.net_size = splitter[opts.pxSplit] - dims.borders;
            dims.net_size2 = splitter[opts.pxFixed] - dims.borders2;
            // Bail if splitter isn't visible or content isn't there yet
            if( dims.net_size <= 0 || dims.net_size2 <= 0 ) { return; }
            if(isNaN(size)) {
                size = (!(opts.sizeRight||opts.sizeBottom)? this.panes[0].el[0][opts.pxSplit] : 
                            dims.borders-this.panes[0].el[0][opts.pxSplit]-dims.bar);
            }
            this.split(size);
        }
        
        /**
         * Constructor of splitter elements
         */
        function init(opts) {
            opts = $.extend({}, defaults, opts || {});
            var vh = opts.type,
                sp = splitters[vh];
            if(!sp) {
                sp = splitters[defaults.type];
            }
            opts = $.extend(opts, sp);
            return this.each(function() {
                var splitter = $(this).css({position: "relative"}),
                    panels = $(">*", this),
                    logger = opts.logger,
                    d = '<div></div>',
                    panes = [{pane: opts.side1},
                             {pane: opts.side2}],
                    dims = {},
                    bar,instance;
                
                if(logger){logger.info('building ' + opts.name + ' splitter panel');}
                panes[0].el = $(panels[0] || d).css(csspanels); // left  or top
                panes[1].el = $(panels[1] || d).css(csspanels); // right or bottom
                bar = $(panels[2] || d).css("z-index", "100");
                splitter.html('').append(panes[0].el).append(bar).append(panes[1].el);
                
                // Cache several dimensions for speed, rather than re-querying constantly
                instance = {
                        'container': splitter,
                        'options': opts,
                        'bar': bar,
                        'dims': dims,
                        'panes': panes,
                        'elems': $([panes[0].el,panes[1].el]),
                        'split': resplit,
                        'barpos': bar_position
                };
                $.data(this,'splitter',instance);
                
                bar.addClass(opts.splitbarClass)
                   .attr({unselectable: "on"})
                   .css({position: "absolute", "user-select": "none",
                       "-webkit-user-select": "none",
                       "-khtml-user-select": "none",
                       "-moz-user-select": "none"})
                   .bind("mousedown", $.proxy(startMove,instance));
                
                instance.Move = $.proxy(Move,instance);
                instance.endMove = $.proxy(endMove,instance);
                // Use our cursor unless the style specifies a non-default cursor
                if ( /^(auto|default|)$/.test(bar.css("cursor")) ) {
                    bar.css("cursor", opts.cursor);
                }

                // Cache several dimensions for speed, rather than re-querying constantly
                dims.bar = bar[0][opts.pxSplit];
                dims.borders = dimSum(splitter, "border"+opts.side1+"Width", "border"+opts.side2+"Width");
                dims.borders2 = dimSum(splitter, "border"+opts.side3+"Width", "border"+opts.side4+"Width");
                $.each(panes, function(){
                    var pane = this.pane;
                    this.min = opts["min"+pane] || dimSum(this.el, "min-"+opts.split);
                    this.max = opts["max"+pane] || dimSum(this.el, "max-"+opts.split) || 9999;
                    this.init = opts["size"+pane]===true ?
                            parseInt($.curCSS(this.el[0],opts.split)) : opts["size"+pane];
                });

                // Determine initial position, get from cookie if specified
                var initPos = panes[0].init;
                if(!isNaN(panes[1].init))  {// recalc initial B size as an offset from the top or left side
                    initPos = this[opts.pxSplit] - dims.borders - panes[1].init - dims.bar;
                }
                if(opts.cookie && $.cookie) {
                    var ckpos = parseInt($.cookie(opts.cookie));
                    if ( !isNaN(ckpos) ) {
                        initPos = ckpos;
                    }
                    $(window).bind("unload", function(){
                        var state = String(bar.css(opts.origin));   // current location of splitbar
                        $.cookie(opts.cookie, state, {expires: opts.cookieExpires || 365, 
                            path: opts.cookiePath || document.location.pathname});
                    });
                }
                if(isNaN(initPos) ) { // King Solomon's algorithm
                    initPos = Math.round((splitter[0][opts.pxSplit] - splitter._PBA - bar._DA)/2);
                }

                // Resize event handler; triggered immediately to set initial position
                splitter.bind("resize", $.proxy(splitterResize, instance))
                        .trigger("resize" , [initPos]);
                
                /*
                 * Bind to resizing window
                 */
                $(window).bind("resize", function(){
                    splitter.trigger("resize"); 
                });
                if(logger){logger.info('finished building ' + opts.name + ' splitter panel');}
            });
        }
            
        return {
            'init': init
        };
    }());
    
    
    // extend plugin scope
    $.fn.extend({
        splitter: $.splitter.init
    });
    
}(jQuery));
