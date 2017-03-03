
Ext.define('ags.group.NotesWidget' ,{
    extend: 'Ext.panel.Panel',
	requires: [

	],

	initComponent: function(){


		 Ext.apply(this, {
			title : 'Notes',
			xxheight: HEIGHT,
  			xxlayout: "border",
			items: [
				{xtype:"textarea"}


			]
		});
		this.callParent();
	}



});
