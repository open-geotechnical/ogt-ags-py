
Ext.define('ags.viewer.GroupGrid' ,{
    extend: 'Ext.grid.Panel',
	requires: [
		//"Ags.abbrev.AbbrevsStore"
	],

	initComponent: function(){
		 Ext.apply(this, {
			deadheight: HEIGHT,
			listeners: {
				select: function(obj, rec, opts){

				}
			}
		});
		this.callParent();
	}

});