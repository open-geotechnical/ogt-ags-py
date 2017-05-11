
Ext.define('ags.group.GroupsGrid' ,{
    extend: 'Ext.grid.Panel',
	requires: [
		//"Ags.abbrev.AbbrevStore"
	],

	initComponent: function(){
		 Ext.apply(this, {
			title : 'Groups Index',
			header: false,
			store: Ext.getStore("groups"),
			height: HEIGHT,
            features: [
                Ext.create('Ext.grid.feature.Grouping', {
                    groupHeaderTpl: '{name}',
                    hideGroupedHeader: true,
                    startCollapsed: false,
                    id: "ags4-class-grouping"
                })
            ],
			columns: [
				{header: 'Group', dataIndex: 'group_code', flex: 1, menuDisabled: true, sortable: true, renderer: R.bold},
				{header: 'Parent', dataIndex: 'parent', flex: 1, menuDisabled: true, sortable: true, renderer: R.bold},
				{header: 'Child', dataIndex: 'child', flex: 1, menuDisabled: true, sortable: true, renderer: R.bold},
				{header: 'Description', dataIndex: 'group_description', flex: 3, menuDisabled: true, sortable: true},
				{header: 'Class',  dataIndex: 'class',  flex: 2, menuDisabled: true, sortable: true}

			],
			tbar: [
			    {xtype: "button", text: "Group by Class", enableToggle: true, pressed: true,
			        handler: function(){
			            Ext.getById("ags4-class-grouping").disable();
                    }
			     }
			],

			dockedItems: [{
                    xtype: 'pagingtoolbar',
                    store: Ext.getStore("groups"),
                    dock: 'bottom',
                    displayInfo: true
			}],

			listeners: {
				select: function(obj, rec, opts){
					//console.log("yes", rec, rec.get("group_code"));
					var sto = Ext.getStore("headings");

					//console.log("proxy", proxy);
					sto.getProxy().url = "/ags4/group/" + rec.get("group_code") + ".json";
					sto.load()

				},
				itemdblclick: function(obj, rec, opts){
                    console.log("YIPEE", rec, rec.get("group_code"));
				}
			}
		});
		this.callParent();
	}



});
