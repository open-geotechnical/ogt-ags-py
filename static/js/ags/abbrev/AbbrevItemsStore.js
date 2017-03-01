
Ext.define('ags.abbrev.AbbrevItemsStore', {
	extend: 'Ext.data.Store',
	requires: [
       //'ags.model.AbbrevItem'
    ],
	constructor: function(){
		Ext.apply(this, {
			model: 'ags.model.AbbrevItem',
			storeId: "abbrev_items",
			pageSize: 2000,
			autoLoad: false,
			proxy: {
				type: 'ajax',
				reader: {
					type: 'json',
					root: "abbreviation.items",
					idProperty: 'item',
					sstotalProperty: 'code_count'
				}
			}
		});
		this.callParent();
	}
});