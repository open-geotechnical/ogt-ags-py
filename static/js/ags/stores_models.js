
Ext.define('ags.model.Abbrev', {
    extend: 'Ext.data.Model',
    fields: [
		'head_code',
		'description',
		'group'
	]
});

Ext.define('ags.model.AbbrevItem', {
    extend: 'Ext.data.Model',
    fields: [
		'item',
		'description',
		"date_added",
		"added_by",
		"status"
	]
});

Ext.define('ags.model.Group', {
    extend: 'Ext.data.Model',
    fields: [
		'group_code',
		'group_description',
		'class',
		'parent',
		'child'
	]
});

Ext.define('ags.model.Heading', {
    extend: 'Ext.data.Model',
    fields: [
		'head_code',
		'head_description',
		'data_type',
		'unit',
		'example',
		'status',
		'sort',
		'rev_date',

	]
});


Ext.create("ags.abbrev.AbbrevsStore", {});
Ext.create("ags.abbrev.AbbrevItemsStore", {});

Ext.create("ags.group.GroupsStore", {});
Ext.create("ags.group.HeadingsStore", {});
