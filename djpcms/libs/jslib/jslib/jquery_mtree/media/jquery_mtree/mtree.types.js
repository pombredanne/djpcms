
(function ($) {
    $.mtree.plugin("types", {
        defaults : {
            // where is the type stores (the rel attribute of the LI element)
            type_attr : "rel",
            types: {
                "default" : {
                    max_children: -1,
                    max_depth: -1,
                    open_icon: 'ui-icon ui-icon-folder-open',
                    closed_icon: 'ui-icon ui-icon-folder-collapsed'
                },
                "file": {
                    max_children  : 0,
                    open_icon: 'ui-icon ui-icon-document',
                    closed_icon: 'ui-icon ui-icon-document'
                }
            }
        },
        extensions : {
            //
            _make_inner: function(obj,js) {
                if(js && js.type) {
                    obj.attr(this.settings().types.type_attr,js.type);
                }
                return this.__super(obj,js);
            },
            // Override the get_type on node
            _get_type : function(obj) {
                var s = this.settings().types,
                    d = s.types['default'];
                obj = this.node(obj);
                if(!obj || !obj.length) { return d; }
                return s.types[obj.attr(s.type_attr)] || d;
            }
        }
    });
}(jQuery));
        