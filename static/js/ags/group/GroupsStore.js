
Ext.define('ags.group.GroupsStore', {
	extend: 'Ext.data.Store',
	requires: [
       //'Ags.model.Abbrev'
    ],
	constructor: function(){
		Ext.apply(this, {
			model: 'ags.model.Group',
			storeId: "groups",
			groupField: 'class',
			sssorters: [ {
				property: 'dated',
				direction: 'DESC'
			}],
			deadsortInfo: {
				property: 'code',
				direction: 'DESC'
			},
			//groupField: "group",
			pageSize: 1000,
			autoLoad: true,
			proxy: {
				type: 'ajax',
				url: "/ags4/groups_list.json",
				reader: {
					type: 'json',
					root: "groups_list",
					idProperty: 'group_code',
					sstotalProperty: 'code_count'
				}
			}
		});
		this.callParent();

	}
});
