

Ext.define('ags.viewer.AGSViewer' ,{
    extend: 'Ext.panel.Panel',
	requires: [
		//"Ags.abbrev.MetaStore"
	],

	initComponent: function(){


		 Ext.apply(this, {
		 	renderTo: "widget_div",
			title : 'File ',
			height: HEIGHT,
  			layout: "border",

  			tbar: [
  				{text: "Open Example", scope: this, handler: this.select_example},
  				"-",
  				{text: "Upload AGS", scope: this, handler: this.upload_dialog},
  				"->",
  				{text: "Clear", scope: this, handler: this.clear_all},

  			],


			items: [
				this.get_tab_panel()
			]
		});
		this.callParent();

		this.load_example("01-temperature_measuring_point_4_0.ags");
	},

	get_tab_panel: function(){
		if(!this._tabpanel){
			this._tabpanel = Ext.create("Ext.tab.Panel", {
				flex: 1,
				region: "center"
			});
		}
		return this._tabpanel
	},

	clear_all: function(){
		var tabPanel = this.get_tab_panel();
		tabPanel.removeAll();
		this.setTitle("File: &lt;none&gt;")
    },

	load_example: function(file_name){

		// show loding message
		Ext.MessageBox.wait('Loading...');

		// nuke existing tabs
		this.clear_all();

		// make server request
		Ext.Ajax.request({

			scope: this,
			url: '/ajax/ags/4/parse',
			method: "GET",
			params: {
				example: file_name
			},

			success: function(response){

				// decode json string
				var data = Ext.decode(response.responseText);

				this.setTitle("File: " + data.document.file_name);

				var groups = data.document.groups;
				var tabPanel = this.get_tab_panel();

				// Loops groups and add tabs for each group
				var grp_len = groups.length; // optimize
				for(var i = 0; i < grp_len; i++){

					var tab = Ext.create("ags.viewer.GroupView", {});
                    tab.load_group(groups[i])
					tabPanel.add(tab)
					if(i == 0){
						// Make first tab active wich should always be PROJ ??
						tabPanel.setActiveTab(tab);
					}
				}

				// Add source tab
				var src_tab = Ext.create("ags.viewer.RawDataView", {});
				src_tab.load_doc(data.document);
				tabPanel.add( src_tab );

				Ext.MessageBox.hide();
			},
			failure: function(xxx){
				alert("TODO: throw tantrum as ajax failer in AGSViewer.js ;-(");
				Ext.MessageBox.hide();
			}

		});

	},

	select_example: function(){
		var d = Ext.create("ags.examples.ExamplesDialog", {});
		d.on("OPEN", function(fn){
			this.load_example(fn);
		}, this)
		d.load_show();

	},

	upload_dialog: function(){
    		var d = Ext.create("ags.viewer.UploadDialog", {});
    		d.on("OPEN", function(fn){
    			this.load_example(fn);
    		}, this)
    		d.show();
    }

});