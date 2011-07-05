/**
 * djpcms - dataTable integration utilities
 */

(function($) {
    /**
     * DJPCMS Decorator for Econometric ploting
     */
    if($.djpcms && $.fn.dataTable) {
        
        $.djpcms.dataTable = {};
        
        /**
         * A tablesorter widget for enabling actions on rows and
         * different views across columns.
         */
        $.djpcms.dataTable.add_select_rows = function(tbl,me,opts) {
            var url = opts.url || '.',
                select = $('select',me);
            
            function handle_callback(e,o) {
                $.djpcms.jsonCallBack(e,o,tbl);
            }
            function toggle(chk) {
                chk.each(function() {
                    var el = $(this),
                        tr = el.parents('tr');
                    if(el.is(':checked')) {
                        tr.addClass('ui-state-highlight');
                    }
                    else {
                        tr.removeClass('ui-state-highlight');
                    }
                });
            }
            
            tbl.delegate('.action-check input','click', function() {
                toggle($(this));
            });
            
            select.change(function() {
                if(this.value) {
                    var ids = [],
                        data = $.djpcms.ajaxparams(this.value,{'ids':ids});
                    $('.action-check input:checked',this.table).each(function() {
                        ids.push(this.value);
                    });
                    $.post(url,
                           data,
                           handle_callback,
                           'json')                       
                }
            });
            $('.select_all',me).click(function() {
                toggle($('.action-check input').prop({'checked':true}));
            });
            $('.select_none',me).click(function() {
                toggle($('.action-check input').prop({'checked':false}));
            });
        };
        
        /**
         * Utility function for setting up columns selections based on groups
         */
        $.djpcms.dataTable.addViews = function(tbl,groups) {
            var r = $('div.col-selector'),
                select = $("<select></select>"),
                views = {},
                n = 0,
                initial = false;
            
            $.each(groups, function() {
                var selected = this.cols.join(',.'),
                    opt;
                if(selected) {
                    n+=1;
                    opt = $("<option value='" + this.name + "'>" + this.display + "</option>");
                    if(this.initial && !initial) {
                        initial = this.name;
                        opt.attr('selected','selected');
                    }
                    select.append(opt);
                    views[this.name] = '.'+selected;
                }
            });
            if(n) {
                r.html("<span class='selectors'>Select a view</span>").append(select);
                
                function change_view(oTable) {
                    return function(value) {
                        if(!value) {return;}
                        var fields = views[value],
                            settings = oTable.fnSettings();
                        
                        if(fields) {
                            $.each(settings.aoColumns, function(i,col) {
                                if(fields.indexOf(col.sName) != -1) {
                                    oTable.fnSetColumnVis(i, true, false);
                                }
                                else {
                                    oTable.fnSetColumnVis(i, false, false);
                                }
                            });
                            ColVis.fnRebuild(oTable);
                            //var cols = $('th,td',tbl),
                            //    selected = $(fields,tbl);
                            //cols.hide();
                            //selected.show();
                        }
                    }
                };
                
                select[0].change_view = change_view(tbl);
                
                if(initial) {
                    select[0].change_view(initial);
                }
                select.change(function() {
                    this.change_view(this.value);
                });
            }
        }
        
        $.djpcms.decorator({
            id:"datatable",
            config: {
                selector: 'div.data-table',
                bJQueryUI: true,
                bDeferRender: true,
                "aaSorting": [],
                "sPaginationType": "full_numbers",
                "sDom": '<"H"<"row-selector"><"col-selector">T<"clear">ilrp>t<"F"ip>',
                "oTableTools": {
                    "aButtons": [
                                 "copy",
                                 {
                                     "sExtends":    "collection",
                                     "sButtonText": "Save",
                                     "aButtons":    [ "csv", "xls", "pdf" ]
                                 }
                             ]
                },
                fnRowCallback: function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
                    return nRow;
                }
            },
            to_obj : function(aoData) {
                var obj = {};
                $.each(aoData,function(){
                    obj[this.name] = this.value;
                })
                return obj;
            },
            fnServerData : function ( sSource, aoData, fnCallback, settings ) {
                var info = this.to_obj(aoData),
                    sc = info.iSortingCols,
                    cols = info.sColumns.split(','),
                    instance = settings.oInstance,
                    params = {},
                    i;
                for(i=0;i<sc;i++) {
                    var co = info['iSortCol_'+i];
                    params[cols[co]] = info['sSortDir_'+i];
                }
                if(sc) {
                    var href = window.location.search,
                        hashes = href.slice(href.indexOf('?') + 1).split('&'),
                        vars = {};
                    //$.each(hashes,function() {
                    //    var hash = this.split('=');
                    //    vars[hash[0]] = hash[1];
                    //});
                    params = $.param($.extend(params,vars));
                    window.location.replace(window.location.pathname+'?'+params);
                }
                else {
                    var json = instance.data('datasize');
                    this.updateDraw(settings, json);
                }
            },
            /**
             * djpcms - datatable decorator
             */
            decorate: function($this,config) {
                var opts = config.datatable,
                    that = this;
                $.each($(opts.selector,$this),function() {
                    var elem = $(this),
                        tbl = $('table',elem).hide(),
                        data = elem.data('options') || {},
                        buttons = [];
                    if(tbl.length == 1) {
                        opts = $.extend(true,{},opts,data);
                        if (!opts.sAjaxSource) {
                            opts.fnServerData = $.proxy(that.fnServerData,that);
                        }
                        opts.oTableTools.sSwfPath = $.djpcms.options.media_url+
                            "djpcms/datatables/TableTools/swf/copy_cvs_xls_pdf.swf";
                        
                        
                        function redirect(url) {
                            return function() {
                                window.location.replace(url);
                            }
                        }
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
                        buttons.push("pdf");
                        opts.oTableTools.aButtons = buttons;
                        
                        tbl.dataTable(opts);
                        //
                        // Add Actions on Rows
                        if(elem.data('actions')) {
                            var s,
                                actions = elem.data('actions'), 
                                r = $('div.row-selector',elem).html(
                            "<span class='selectors'>Select:" +
                            " <a class='select_all' href='#'>All</a>," +
                            "<a class='select_none' href='#'>None</a></span>");
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
                        tbl.show();
                    }
                });
            } 
        });
    }
}(jQuery));