
Ext.define('ags.group.GroupView' ,{
    extend: 'Ext.panel.Panel',
	requires: [
		//"Ags.abbrev.MetaStore"
	],

	initComponent: function(){


		 Ext.apply(this, {
			title : 'Group ',
			height: HEIGHT,
  			layout: "border",
			items: [
				Ext.create("ags.group.HeadingsGrid", {flex: 3, region: "center"}),
				{xtype: "tabpanel", flex: 1, region: "east",
				    items: [
				        Ext.create("ags.group.NotesWidget", {}),
				        Ext.create("ags.group.PreviewForm", {flex: 1, region: "east"})
                    ]
                }
			]
		});
		this.callParent();
	}



});
