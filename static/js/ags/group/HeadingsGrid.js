
Ext.define('ags.group.HeadingsGrid' ,{
    extend: 'Ext.grid.Panel',
	requires: [
		//"Ags.abbrev.AbbrevStore"
	],

	initComponent: function(){
		 Ext.apply(this, {
			ddtitle : 'Hedings Index',
			store: Ext.getStore("headings"),
			height: 100,

			columns: [
				{header: ' ', dataIndex: 'sort', width: 20, menuDisabled: true, sortable: true},
				{header: 'Heading', dataIndex: 'head_code', flex: 1, menuDisabled: true, sortable: true, renderer: R.bold},
				{header: 'Unit', dataIndex: 'unit', width: 50, menuDisabled: true, sortable: true},
				{header: 'Type', dataIndex: 'data_type', width: 50, menuDisabled: true, sortable: true},
				{header: 'Description', dataIndex: 'description', flex: 3, menuDisabled: true, sortable: true},
				{header: 'Added',  dataIndex: 'date_added',  flex: 1, menuDisabled: true, sortable: true}

			],

			dockedItems: [{
                    xtype: 'pagingtoolbar',
                    store: Ext.getStore("headings"),
                    dock: 'bottom',
                    displayInfo: true
			}],

			listeners: {
				DEADDDDDselect: function(obj, rec, opts){
					console.log("yes", rec, rec.get("heading"));
					var sto = Ext.getStore("abbrev_items");
					//console.log("detch", rec);
					//var sto = Ext.getStore("abbrev_items");

					//var proxy = Ext.getStore("abbrev_items").getProxy()
					//console.log("proxy", proxy);
					sto.getProxy().url = "/ags/4/abbrev/" + rec.get("heading");
					sto.load()
				}
			}
		});
		this.callParent();
	}



});