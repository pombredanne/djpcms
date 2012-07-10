/*jslint browser: true */
/*global jQuery: true, ColVis: true */

/**
 * djpcms - dataTable integration utilities
 */

(function ($) {
	"use strict";
    /**
     * DJPCMS Decorator for jQuery dataTable plugin
     */
	
	$.djpcms.decorator({
		name: "color_number",
        config: {
        	selector: 'tr .color'
        },
        decorate: function(elem,config) {
            $(config.color_number.selector,elem).each(function() {
                var el = $(this),
                    val = el.html();
                try {
                    val = parseFloat(val);
                    if(val < 0) {
                        el.addClass('ui-state-error-text');
                    }
                    if(el.hasClass('arrow') && val === val) {
                        var ar = $('<span></span>').css({'margin-right':'.3em',
                                                     'float':'right'});
                        val > 0 ? ar.addClass('ui-icon ui-icon-arrowthick-1-n') :
                                  ar.addClass('ui-icon ui-icon-arrowthick-1-s');
                        el.append(ar);
                    }
                }catch(e){}
            });
        }});
        
        
    if ($.djpcms && $.fn.dataTable) {
        
    	// djpcms dataTable handler
        $.djpcms.dataTable = {};
        
        // from
        // http://www.datatables.net/forums/discussion/6106/conditionally-set-column-text-color/p1
        $.djpcms.dataTable.fnRowCallback = function (nRow, aData, iDisplayIndex, iDisplayIndexFull) {
            /* numbers less than or equal to 0 should be in red text */
            if (parseFloat(aData[4]) <= 0) {
                $('td:eq(4)', nRow).addClass('redText');
            }
            return nRow;
        };
        
        $.fn.dataTableExt.oApi.fnSetFilteringDelay = function (oSettings, iDelay) {
            /*
             * Inputs:      object:oSettings - dataTables settings object - automatically given
             *              integer:iDelay - delay in milliseconds
             * Usage:       $('#example').dataTable().fnSetFilteringDelay(250);
             * Author:      Zygimantas Berziunas (www.zygimantas.com) and Allan Jardine
             * License:     GPL v2 or BSD 3 point style
             * Contact:     zygimantas.berziunas /AT\ hotmail.com
             */
            var that = this;
            iDelay = (typeof iDelay === 'undefined') ? 250 : iDelay;
            
            this.each(function (i) {
                $.fn.dataTableExt.iApiIndex = i;
                var $this = this, 
                    oTimerId = null, 
                    sPreviousSearch = null,
                    anControl = $('input', that.fnSettings().aanFeatures.f);
                
                anControl.unbind('keyup').bind('keyup', function () {
                    if (sPreviousSearch === null || sPreviousSearch !== anControl.val()) {
                        window.clearTimeout(oTimerId);
                        sPreviousSearch = anControl.val();  
                        oTimerId = window.setTimeout(function () {
                            $.fn.dataTableExt.iApiIndex = i;
                            that.fnFilter(anControl.val());
                        }, iDelay);
                    }
                });
                
                return this;
            });
            return this;
        };

        
        /**
         * A tablesorter widget for enabling actions on rows and
         * different views across columns.
         */
        $.djpcms.dataTable.add_select_rows = function (tbl, me, opts) {
            var url = opts.url || '.',
                select = $('select', me);
            
            function handle_callback(e, o) {
                $.djpcms.jsonCallBack(e, o, tbl);
            }
            function toggle(chk) {
                chk.each(function () {
                    var el = $(this),
                        tr = el.parents('tr');
                    if (el.is(':checked')) {
                        tr.addClass('ui-state-highlight');
                    } else {
                        tr.removeClass('ui-state-highlight');
                    }
                });
            }
            
            tbl.delegate('.action-check input', 'click', function () {
                toggle($(this));
            });
            
            select.change(function () {
                if (this.value) {
                    var ids = [],
                        data = $.djpcms.ajaxparams(this.value, {'ids': ids});
                    $('.action-check input:checked', this.table).each(function () {
                        ids.push(this.value);
                    });
                    $.post(url,
                           data,
                           handle_callback,
                           'json');                       
                }
            });
            $('.select_all', me).click(function () {
                toggle($('.action-check input').prop({'checked': true}));
            });
            $('.select_none', me).click(function () {
                toggle($('.action-check input').prop({'checked': false}));
            });
        };
        
        /**
         * Utility function for setting up columns selections based on groups
         */
        $.djpcms.dataTable.addViews = function (tbl, groups) {
            var r = $('div.col-selector'),
                select = $("<select></select>"),
                views = {},
                n = 0,
                initial = false;
            
            function change_view(oTable) {
                return function (value) {
                    if (!value) {
                    	return;
                    }
                    var fields = views[value],
                        settings = oTable.fnSettings();
                    
                    if (fields) {
                        $.each(settings.aoColumns, function (i, col) {
                            if (fields.indexOf(col.sName) !== -1) {
                                oTable.fnSetColumnVis(i, true, false);
                            } else {
                                oTable.fnSetColumnVis(i, false, false);
                            }
                        });
                        ColVis.fnRebuild(oTable);
                        //var cols = $('th,td',tbl),
                        //    selected = $(fields,tbl);
                        //cols.hide();
                        //selected.show();
                    }
                };
            }
        	
            $.each(groups, function () {
                var cols = this.cols,
                    selected = $.isArray(cols) ? this.cols.join(',.') : cols,
                    opt;
                if (selected) {
                    n += 1;
                    opt = $("<option value='" + this.name + "'>" + this.display + "</option>");
                    if (this.initial && !initial) {
                        initial = this.name;
                        opt.attr('selected', 'selected');
                    }
                    select.append(opt);
                    views[this.name] = '.' + selected;
                }
            });
            if (n) {
                r.html("<span class='selectors'>Select a view</span>").append(select);
                
                select[0].change_view = change_view(tbl);
                
                if (initial) {
                    select[0].change_view(initial);
                }
                select.change(function () {
                    this.change_view(this.value);
                });
            }
        };
        
        /*
         * djpcms - datatable decorator
         */
        $.djpcms.decorator({
            name: "datatable",
            config: {
                selector: 'div.data-table',
                fnRowCallbacks: [],
                options: {
                    //bJQueryUI: true,
                    bDeferRender: true,
                    "aaSorting": [],
                    "sPaginationType": "full_numbers",
                    "sDom": '<"H"<"row-selector"><"col-selector">T<"clear">ilrp>t<"F"ip>',
                    "oTableTools": {
                        "aButtons": [
                            "copy",
                            {
                            	"sExtends": "collection",
                                "sButtonText": "Save",
                                "aButtons": [ "csv", "xls", "pdf" ]
                            }
                        ]
                    },
                    fnRowCallback: function (nRow, aData, iDisplayIndex, iDisplayIndexFull) {
                        $.each($.djpcms.options.datatable.fnRowCallbacks, function (i, func) {
                            func(nRow, aData, iDisplayIndex, iDisplayIndexFull);
                        });
                        return nRow;
                    }
                }
            },
            to_obj: function (aoData) {
                var obj = {};
                $.each(aoData, function () {
                    obj[this.name] = this.value;
                });
                return obj;
            },
            /*
             * The function used to load the data
             */
            fnServerData: function (sSource, aoData, fnCallback, settings) {
                var info = this.to_obj(aoData),
                    sc = info.iSortingCols,
                    cols = info.sColumns.split(','),
                    instance = settings.oInstance,
                    params = {},
                    vars = {},
                    href = window.location.search,
                    i,
                    co,
                    hashes;
                for (i= 0; i< sc; i++) {
                    co = info['iSortCol_' + i];
                    params[cols[co]] = info['sSortDir_' + i];
                }
                if (sc) {
                    hashes = href.slice(href.indexOf('?') + 1).split('&');
                    //$.each(hashes,function() {
                    //    var hash = this.split('=');
                    //    vars[hash[0]] = hash[1];
                    //});
                    params = $.param($.extend(params,vars));
                    window.location.replace(window.location.pathname + '?' + params);
                } else {
                    this.updateDraw(settings, instance.data('datasize'));
                }
            },
            ajaxServerData: function ( sSource, aoData, fnCallback ) {
    			$.ajax({
    				"dataType": 'json', 
    				"type": "POST", 
    				"url": sSource, 
    				"data": aoData, 
    				"success": fnCallback
    			});
    		},
            /**
             * Decorate function
             */
            decorate: function($this, config) {
                var datatable = config.datatable,
                    that = this;
                function redirect(url) {
                    return function () {
                        window.location.replace(url);
                    }
                }
                // Loop over each selected table element
                $.each($(datatable.selector, $this),function () {
                    var elem = $(this),
                        tbl = $('table',elem).addClass('main display'),
                        data = elem.data('options') || {},
                        buttons = [],
                        opts;
                    if(tbl.length == 1) {
                        opts = $.extend(true,{},datatable.options,data);
                        if (opts.sAjaxSource) {
                        	opts.fnServerData = that.ajaxServerData;
                        } else {
                            opts.fnServerData = $.proxy(that.fnServerData,that);
                        }
                        opts.oTableTools.sSwfPath = $.djpcms.options.media_url+
                            "djpcms/datatables/TableTools/swf/copy_cvs_xls_pdf.swf";
                        //
                        // Add tools to table tools
                        if(elem.data('tools')) {
                            $.each(elem.data('tools'),function() {
                                var b = {
                                    sExtends: "text",
                                    sButtonText:this.display,
                                    sToolTip:this.title,
                                    fnClick: function(nButton, oConfig, oFlash) {
                                        oConfig.send();
                                    }
                                }
                                buttons.push(b);
                                if(this.ajax) {
                                    b.send = $.djpcms.ajax_loader_from_tool(this);
                                }
                                else {
                                    b.send = redirect(this.url);
                                }
                            });
                        }
                        buttons.push("csv");
                        //buttons.push("pdf");
                        opts.oTableTools.aButtons = buttons;
                        
                        // Create the datatable
                        tbl.dataTable(opts).fnSetFilteringDelay(1000);
                        //
                        // Add Actions on Rows
                        if(elem.data('actions')) {
                            var s,
                                actions = elem.data('actions'), 
                                r = $('div.row-selector',elem).html(
                            "<span class='selectors'>Select:" +
                            " <a class='select_all' href='#'>All</a>," +
                            " <a class='select_none' href='#'>None</a></span>");
                            s = $("<select><option value=''>Actions</option></select>").appendTo(r);
                            $.each(actions.choices, function() {
                                s.append("<option value='" + this[0] + "'>" + this[1] + "</option>");
                            });
                            $.djpcms.dataTable.add_select_rows(tbl,r,actions);
                        }
                        
                        //
                        // Add column grouping
                        if(elem.data('groups')) {
                            $.djpcms.dataTable.addViews(tbl,elem.data('groups'));
                        }
                        $('.dataTables_filter input').addClass('ui-widget-content');
                        tbl.width('100%');
                        elem.show();
                    }
                });
            } 
        });
        
        $.djpcms.options.datatable.fnRowCallbacks.push(function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
        	$(nRow).djpcms();
        });
    }
}(jQuery));