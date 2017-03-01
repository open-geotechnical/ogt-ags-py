
Ext.define('ags.abbrev.AbbrevView' ,{
    extend: 'Ext.grid.Panel',
	requires: [
		//"Ags.abbrev.MetaStore"
	],

	initComponent: function(){
		 Ext.apply(this, {
			title : 'Abbreviations',
			height: HEIGHT,
  			store: Ext.getStore("abbrev_items"),
			columns: [
				{header: 'Code',  dataIndex: 'item',  flex: 1, hideMenu: true, renderer: R.bold},

				{header: 'Description', dataIndex: 'description', flex: 4, menuDisabled: true, sortable: true},
				{header: 'Date Added', dataIndex: 'date_added', flex: 1, menuDisabled: true, sortable: true},
				{header: 'Added By', dataIndex: 'added_by', flex: 1, menuDisabled: true, sortable: true},
				{header: 'Status', dataIndex: 'status', flex: 1, menuDisabled: true, sortable: true}
			],

			dockedItems: [{
				xtype: 'pagingtoolbar',
				store: Ext.getStore("abbrev_items"),
				dock: 'bottom',
				displayInfo: true
			}],
		});
		this.callParent();
	}
        
        
    
});