
(function($) {
    
    $.djpcms.addDecorator({
       id: 'bsmselect',
       decorate: function(self, config) {
           $('select.bsmSelect',self).bsmSelect({
               addItemTarget: 'bottom',
               animate: true,
               highlight: true,
               plugins: [
                 $.bsmSelect.plugins.sortable({ axis : 'y', opacity : 0.5 },
                         { listSortableClass : 'bsmListSortableCustom' }),
                 $.bsmSelect.plugins.compatibility()
               ]
           });
       }
    });
    
}(jQuery));