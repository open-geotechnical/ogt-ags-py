
Ext.define('ags.group.NotesWidget' ,{
    extend: 'Ext.grid.Panel',
	requires: [

	],

	initComponent: function(){


		 Ext.apply(this, {
			title : 'Notes',
			store: Ext.getStore("notes"),
			height: 100,

			columns: [

				{header: 'Note', dataIndex: 'note', flex: 1, menuDisabled: true, sortable: true}
			]
		});
		this.callParent();
	}



});
