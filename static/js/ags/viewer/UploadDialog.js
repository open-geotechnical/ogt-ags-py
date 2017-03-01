Ext.define('ags.viewer.UploadDialog' ,{
    extend: 'Ext.window.Window',
	requires: [
		//"Ags.abbrev.AbbrevsStore"
	],
	file_name: null,

	initComponent: function(){
		 Ext.apply(this, {
			modal: true,

			width: 600,
			layout: "fit",
			title: "Upload File",

			items: [
				{xtype: "form",
					standardSubmit: false,

					items: [
							{
								xtype: 'filefield',
								name: 'ags_file',
								fieldLabel: 'AGS File',
								labelWidth: 60,
								msgTarget: 'side',
								allowBlank: false,
								anchor: '100%',
								buttonText: 'Select...'
							}
					]
				}
			],
			buttons: [
				{text: "Cancel", handler: this.close, scope: this},
				{text: "Upload",  scope: this, handler: function() {

						var f = this.down("form").getForm();
						f.submit({
							url: "/ajax/ags/4/parse",
                            method: "POST",
							headers: {'Content-Type': 'multipart/form-data'},
							isUpload: true
						});
					}
				},
			]

		});
		this.callParent();
	},



});