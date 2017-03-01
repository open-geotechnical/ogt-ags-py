Ext.define('ags.examples.ExamplesDialog' ,{
    extend: 'Ext.window.Window',
	requires: [
		//"Ags.abbrev.AbbrevsStore"
	],
	file_name: null,

	initComponent: function(){
		 Ext.apply(this, {
			modal: true,
			height: HEIGHT - 100,
			width: 500,
			layout: "border",
			title: "Select Example",

			items: [
				this.get_grid()
			],
			buttons: [
				{text: "Cancel", handler: this.close, scope: this},
				{text: "Open", handler: this.select_file, scope: this,
					disabled: true, id: "example_select_button"},
			]

		});
		this.callParent();
	},

	load_show: function(){
		this.get_grid().getStore().load();
		this.show();

	},

	get_grid: function(columns, store){

		if(!this._grid){
			this._grid = Ext.create("Ext.grid.Panel", {
				autoHeight: true,
				region:"center",
				columns: [
					{text: "File Name", dataIndex: "file_name", flex: 1}
				],
				store: Ext.create("Ext.data.JsonStore", {
						proxy: {
							type: 'ajax',
							url: '/ajax/ags/4/examples',
							reader: {
								type: 'json',
								root: 'examples',
								idProperty: 'file_name'
							}
						},
						fields: [
							{name: "file_name"}
						]
				}),
				listeners: {
				 	scope: this,
					selectionchange: this.selection_changed
				}
			});
		}
		return this._grid;
    },

	selection_changed: function(foo, selected, opts){
		this.down("#example_select_button").setDisabled( selected.length == 0 );
	},

	select_file: function(){
		var recs = this.get_grid().getSelectionModel().getSelection();
		this.hide();
		this.fireEvent("OPEN", recs[0].data.file_name);
		this.close();
		this.destroy();
	}



});