/**
 * A table plugin for displying a splitter windows with the tree
 * on the left hand side a table displaying details on
 * the right-hand side.
 * 
 * JSON Data.
 * 
 * fields: an array of objects or strings. If objects they should be of the form
 *  {name: String, description: String}
 */
/*global jQuery*/
(function ($) {
    
    /**
     * Function invoked when a new table is required. Usually when a new node goes into focus
     */
    $.mtree.render_table_from_node = function(instance) {
        //
        // When node is selected displays children on the table
        if(!instance.data.ui.last_selected) {return;}
        var table = instance.data.table,
            logger = instance.logger(),
            selected = instance.data.ui.last_selected,
            id = selected.attr('id'),
            view = instance.current_view(),
            tbl = instance.table(),
            tbody = $('tbody',tbl).empty(),
            thead = $('thead tr.summary',tbl).empty(), cd;
        logger.debug('mtree refreshing table for node '+id);
        
        cd = table.tbody[id];
        thead.append($('<th class="node-name mtree-column">').append(cd['node-name']));
        $.each(view.fields, function(i,field) {
            thead.append('<th class="'+field+'" mtree-colum">'+cd[field]+'</th>');
        });
        $.each(instance.children(selected),function(idx,child){
            cd = table.tbody[child.id];
            var inner = $('<a = href="#"></a>')
                            .append(cd['node-name'])
                            .prepend("<ins class='ui-icon'>&#160;</ins>"),                      
                tr = $('<tr>').appendTo(tbody);
            tr.append($('<td class="node-name mtree-column">').append(inner));
            $.each(view.fields, function(i,field) {
                tr.append('<td class="'+field+'" mtree-colum">'+cd[field]+'</td>');
            });
            tr.appendTo(tbody);
        });
        if($.tablesorter) {
            tbl.trigger('update');
        }
    };
    
    if(!$.mtree.build_table_header) {
        /**
         * Build the plugin header if there are more than one view
         */
        $.mtree.build_table_header = function(that) {
            var t = that.data.table;
                logger = that.logger(),
                views = t.views;
                select = $('<select>'),
                div = $('<div class="views"><span>Select a view</span></div>').append(select);
                header = $('.mtree-table-header',that.container());
            $.each(t.views, function(i,view) {
                select.append('<option value="' + i + '">' + view.name + '</option>');
            });
            header.append(div);
            select.change(function() {
                that.select_view(this.value);
            });
        };
        
    }
    
    $.mtree.plugin("table", {
        defaults : {
            name: 'name',
            resizable: true,
            min_height: '300px', // minimum height of the tree table
            minLeft: 120,
            sizeLeft: 200,
            minRight: 150,
            breadcrumbs: false,
            showroot: true,
            views: [],
            current: -1
        },
        init_instance : function () {
            var table = this.data.table,
                that = this;
            table.tbody = {};
            this.container()
                .addClass('tableview')
                .bind('select_node.mtree', function(event, data) {
                    $.mtree.render_table_from_node(data.inst);
                });
        },
        extensions: {
        	// Override init method to create a splitter panel for the tree and the table
        	_initial_layout: function() {
                var self = this.container(),
                    s = this.settings().table;
                    main = $('<div class="mtree-table-main"></div>');
                self.empty()
                    .append('<div class="mtree-table-header ui-widget-header"></div>')
                    .append(main);
                main.append('<div class="mtree-tree"><div class="top ui-widget-header"></div><div class="main"><ul></ul></div></div>')
                	.append('<div class="mtree-table"><table></table></div>')
                	.css({'min-height':s.min_height});
                
                this.data.table.name = s.name;
                // apply splitter if available and if resizable is set to true
                if(s.resizable && $.fn.splitter) {
                	main.splitter({
                	    logger: this.settings().logger,
                		type: 'v',
                		sizeLeft: s.sizeLeft,
                		minLeft: s.minLeft,
                		minRight: s.minRight
                	});
                }
        	},
        	_root: function() {
        		return $(".mtree-tree .main",this.container());
        	},
        	_table: function() {
        		return $(".mtree-table table",this.container());
        	},
        	//
        	// Override parse json to retrive views and field information
        	_parse_json: function(obj, js) {
        		if($.isFunction(js)) { 
        			js = js.call(this);
        		}
        		if(obj === -1 && !this.data.table.views) {
        			this.make_table_fields(js);
        		}
        		return this.__super(obj,js);
        	},
        	//
        	// Create the table fields and views.
        	// Fields and views are both arrays of objects
        	_make_table_fields: function(js) {
        		var opts = this.data.table,
        			views,
        			fields,
        			view = false,
        			new_fields = opts.fields = [];
        		    dfields = opts.dfields = {},
        			logger = this.settings().logger;
        		if('views' in js && 'fields' in js) {
        			views = js.views;
        			fields = js.fields;
        		}
        		else if('fields' in js) {
        			fields = js.fields;
        		}
        		else {
        			fields = [];
        		}
        		if(!views) {
        			view = {name:'default', 'fields': []};
        			views = [view];
        		}
        		logger.debug('There are ' + views.length + ' views in table tree');
        		opts.views = views;
        		$.each(fields, function(i,field) {
        			if( typeof field === 'string') {
        				field = {name: field, description: field};
        			}
        			new_fields.push(field);
        			dfields[field.name] = field.description;
        			if(view) {
        				view.fields.push(field.name);
        			}
        		});
        		if(views.length > 1) {
        		    $.mtree.build_table_header(this);
                }
        		this.select_view(0);
        	},
        	//
        	// Select a new view.
        	// When selecting a new view, a new table is rendered.
        	_select_view: function(view) {
        		var opts = this.data.table,
        		    logger = this.logger(),
        		    table = this.table(),
        			tr, fields, field;
        		if(opts.current === view) {return;}
        		logger.info('Change to "'+views[view].name+'" view');
        		opts.current = view;
        		view = this.current_view();
        		dfields = opts.dfields;
        		
        		table.html('<thead><tr class="field-names ui-widget-header"></tr></thead><thead><tr class="summary"></tr></thead><tbody></tbody>');
        		tr = $('thead tr.field-names',table);
        		tr.append('<th class="node-name mtree-column">'+opts.name+'</th>');
        		$.each(view.fields, function(idx,name) {
        			field = dfields[name];
        			field = field ? field : name;
        			tr.append('<th class="' + name + ' mtree-column">'+
        						field+'</th>');
        		});
        		if($.tablesorter) {
                    table.addClass('tablesorter').tablesorter({selectorHeaders: 'thead:first th'});
                }
        		$.mtree.render_table_from_node(this);
        	},
        	//
        	_current_view: function() {
        		var c = this.data.table.current;
        		if(c === -1) {return null;}
        		return this.data.table.views[this.data.table.current];
        	},
        	//
        	// Override node creation so that we process fields values
        	create_node: function(obj, data, position, callback, is_loaded) {
        		var d = this.__super(obj, data, position),
        		    id = d.attr('id'),
        		    table = this.data.table,
        			fields = table.fields,
        			node_fields = data ? data.values || {} : {},
        			node_type = this.get_type(d),
        			tbody = {};
        		// no id
        		if(!id) {
        			id = this.unique_id();
        			d.attr('id',id);
        		}
        		table.tbody[id] = tbody;
        		
        		tbody['node-name'] = this.get_text(d);
        		
        		if($.isArray(node_fields)) {
        		    $.each(fields, function(idx,field) {
                        val = node_fields[idx] || '';
                        tbody[field.name] = val;
                    });
        		}
        		else {
        			$.each(fields, function(idx,field) {
        				val = node_fields[field.name] || '';
        				tbody[field.name] = val;
        			});
        		}
        		if(callback) { callback.call(this, d); }
                return d;
        	}
        }
    });
}(jQuery));
