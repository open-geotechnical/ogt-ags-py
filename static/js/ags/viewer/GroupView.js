
Ext.define('ags.viewer.GroupView' ,{
    extend: 'Ext.panel.Panel',
	requires: [
		//"Ags.abbrev.AbbrevsStore"
	],

	initComponent: function(){
		 Ext.apply(this, {
			//deadheight: HEIGHT,
			layout: "border",
			title: "TITLE",
			tabConfig: {
				tooltip: "tooltip"
			},
			items: [
				this.get_description(),
				this.get_grid()
			]

		});
		this.callParent();
	},


	get_description: function(columns, store){

		if(!this._desc){
			this._desc = Ext.create("Ext.form.field.Display", {name: "description", value: "--",
														region:"north", fieldCls: "ags_group_description"});
		}
		return this._desc;
	},

	get_grid: function(columns, store){

		if(!this._grid){
			this._grid = Ext.create("ags.viewer.GroupGrid", {
			dddheight: HEIGHT - 110,
				autoHeight: true,
				region:"center",
				ssflex: 5,
				columns: [],
				//store: store
			});
		}
		return this._grid;
	},



	load_group: function(grp){

		// Set titles + description
		this.setTitle(grp.group_code);
		this.get_description().setValue(grp.description);

		// Create columns and model
		var headings_len =  grp.headings.length;
		var model_fields = [];
		var col_defs = [];

		for(var c = 0; c < headings_len; c++){
			var h = grp.headings[c];
			var fld = {name: h.head_code, type: "string"}

			if( h.data_type == "DT") {
				fld.type = "date";
			}


			model_fields.push(  fld );

			// col def for grid, also hide data in `geo_data`
			var col = {header: h.head_code + "<br>" + h.description + "&nbsp;" + "<br>" + h.data_type + "&nbsp;",
						dataIndex: h.head_code,
						sortable: true, menuDisabled: true,
						head_code: h.head_code
						};
			col_defs.push(col);
		}
		//console.log(grp.group_code,  h.head_code + ".value");

		var model = this.make_model(model_fields);
		var sto = Ext.create("Ext.data.Store", {model: model});
		for(var di = 0; di < grp.data.length; di++){
			var rd = grp.data[di];
			var	rec = {};
			for(var cd = 0; cd < headings_len; cd++){
				var hhc = grp.headings[cd].head_code;
				if(grp.headings[cd].unit == "DT"){
					rec[hhc] = parse_ags_date(rd[hhc].value);
				}
				rec[hhc] = rd[hhc].value;
			}
			sto.add(rec);
		}
		this.get_grid().reconfigure(sto, col_defs);

	},

	make_model: function(fields){

		return Ext.define('Ags.dymamic.MODEL' + Ext.id(), {
			extend: 'Ext.data.Model',
			fields: fields,
			proxy: {
				type: 'memory',
				reader: {
					type: 'json',
					totalProperty: 'tc',
					root: 'foobar'
				}
			}
		});
	}

});