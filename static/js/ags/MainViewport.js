Ext.define('ags.MainViewport', {
	extend: "Ext.tab.Panel",
	renderTo: "widget_div",
	width: "100%",
	//height: window.innerHeight - 80,
	plain: true,
	dtitle: "AGS 4",
	border: 0,
    layout: 'fit',
    activeTab: 0,
    items: [
			{xtype: "panel", title: "Groups", layout: "column", border: 0, plain: true,
				items: [
					Ext.create("ags.group.GroupsGrid", {columnWidth: 0.3}),
					Ext.create("ags.group.GroupView",  {columnWidth: 0.7, id: "GroupView"})
				]
			}
			 ,
			{xtype: "panel", title: "Abbreviations", layout: "column", border: 0, plain: true,
				items: [
					Ext.create("ags.abbrev.AbbrevsGrid", {columnWidth: 0.5}),
					Ext.create("ags.abbrev.AbbrevView", {columnWidth: 0.5})
				]
			}
        ]
});