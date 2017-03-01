
Ext.define('ags.abbrev.AbbrevsGrid' ,{
    extend: 'Ext.grid.Panel',
	requires: [
		//"ags.abbrev.AbbrevsStore"
	],

	initComponent: function(){
		 Ext.apply(this, {
			title : 'Headings',
			store: Ext.getStore("abbrevs"),
			height: HEIGHT,

			columns: [
				{header: 'Heading',  dataIndex: 'head_code',  flex: 1, menuDisabled: true, sortable: true,
					renderer: R.bold
				},
				{header: 'Description', dataIndex: 'description', flex: 1, menuDisabled: true, sortable: true},
				{header: 'Group', dataIndex: 'group', flex: 1, menuDisabled: true, sortable: true}
			],

			dockedItems: [{
                    xtype: 'pagingtoolbar',
                    store: Ext.getStore("abbrevs"),
                    dock: 'bottom',
                    displayInfo: true
			}],

			listeners: {
				select: function(obj, rec, opts){
					//console.log("yes", rec, rec.get("heading"));
					var sto = Ext.getStore("abbrev_items");
					//console.log("detch", rec);
					//var sto = Ext.getStore("abbrev_items");

					//var proxy = Ext.getStore("abbrev_items").getProxy()
					//console.log("proxy", proxy);
					sto.getProxy().url = "/ajax/ags/4/abbrev/" + rec.get("head_code");
					sto.load()
				}
			}
		});
		this.callParent();
	}
        
        
    
});