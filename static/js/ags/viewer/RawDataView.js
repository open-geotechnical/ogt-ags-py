
Ext.define('ags.viewer.RawDataView' ,{
    extend: 'Ext.tab.Panel',
	requires: [
		//"Ags.abbrev.MetaStore"
	],

	initComponent: function(){
		 Ext.apply(this, {
			title : 'Raw Data',
			layout: "fit",
			items: [
				{title: "Spreadsheet View", layout: "fit",
					items: [
						Ext.create("Ext.grid.Panel", {
										g_name: "raw_grid",
										forceFit: true,
                        				autoHeight: true,
                        				columns: [], // reconfigure later
                        				//store: store // reconfigure later
                        })
					]
				},
				{title: "Raw Text", layout: "fit",
					items: [
						{xtype: "textarea", g_name: "raw_text", fieldCls: "ags_raw_text"}
					]
				}

			]
		});
		this.callParent();
	},


	load_doc: function(doc){

		// stick raw source into text area
		this.down("[g_name=raw_text]").setValue(doc.source);

		// no of lines is the array length.. and some opitz
		var glines = doc.lines;
		var lenny = glines.length;

		// no of cols to create cos we have to arrange
		// guests first and find no of tables
		var cols_length = -1;

		//Snag.. we need to walk through all groups and find max line length of line
		// so  iterate first, find max col and create model
		for(var i = 0; i < lenny; i++) {
			var recs = glines[i].records;
			if( recs != null && recs.length > cols_length ) {
				cols_length = recs.length;
			}
		}
		var col_defs = [{xtype: 'rownumberer'}];
		var model_fields = [];
		for(var i = 0; i < cols_length; i++){
			col_defs.push({header: i + 1, dataIndex: "c_" + i, menuDisabled: true, renderer: this.r_row});
			model_fields.push( {name: "c_" + i, type: "string"} );
		}
		//console.log("c=", col_defs, model_fields);

		var model = this.make_model(model_fields);
		var sto = Ext.create("Ext.data.Store", {model: model});
		for(var di = 0; di < lenny; di++){
			var rd = glines[di].records;

			var	rec = {};
			if(rd != null ){
				for(var cd = 0; cd < rd.length; cd++){
					//var hhc = grp.headings[cd].head_code;
					rec["c_" + cd] = rd[cd];
				}
			}
			//console.log("rec=", rec);
			sto.add(rec);
		}
		this.down("[g_name=raw_grid]").reconfigure(sto, col_defs);

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
	},

	r_row: function(val, meta, rec, rowIdx, colIdx, store){

		var row_type = rec.get("c_0")

		if( row_type == GROUP){
			meta.tdCls = "ags_group_row";

		} else if (row_type == DATA){
			meta.tdCls = "ags_group_data";

		} else if  (row_type == "") { //UNIT || row_type == HEADING || row_type == TYPE) {

		} else {
			meta.tdCls = "ags_group_header";
			//console.log(row_type)
		}
		if(colIdx == 1) {
			meta.style = "font-weight: bold;"
		}
		return val;
	}





});