
Ext.define('ags.group.PreviewForm' ,{
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
				Ext.create('Ext.grid.property.Grid', {
                    deadwidth: 300,

                    source: {
                        "(name)": "Properties Grid",
                        "grouping": false,
                        "autoFitColumns": true,
                        "productionQuality": false,
                        "created": Ext.Date.parse('10/15/2006', 'm/d/Y'),
                        "tested": false,
                        "version": 0.01,
                        "borderWidth": 1
                    },
                    sourceConfig: {
                        borderWidth: {
                            displayName: 'Border Width'
                        },
                        tested: {
                            displayName: 'QA'
                        }
                    }
                })


			]
		});
		this.callParent();
	}



});
