
var icons = {};
icons.red 		= 'map/m_red.png';
icons.yellow 	= 'map/m_yellow.png';
icons.green 	= 'map/m_green.png';
icons.purple 	= 'map/m_purple.png';
icons.orange 	= 'map/m_orange.png';
icons.blue 		= 'map/m_blue.png';

var init_flag = false;
var pending_markers = [];

var curr_idx = -1;

var bug = true;
var edit_mode = false;

var geocoder;
var mapDiv;
var map;
var debugTxt;
var markers = {};

var idx = 0;
var z = 10000;



function set_marker_icons(icon){
	for(var m in markers){
		markers[m].setIcon(icon);
	}
}

//***************************************
//** attach Message
//***************************************
function attach_marker(marker, mId, marker_title){
	//var message = ["This","is","the","secret","message"];
	//alert("no" + number);
	//var infowindow = new google.maps.InfoWindow({
	//				content: title,
	//				size: new google.maps.Size(50,50)
	//});
	//alert("pre click");
	//return
	google.maps.event.addListener(marker, 'click', function() {
		//if(curr_idx > 0){
		//	markers[curr_idx].setIcon( markers[curr_idx].mIco);
		//	QtWidget.marker_unselected(curr_idx, markers[curr_idx].mLocationId);
		//}
		//curr_idx = marker.mIdx;
		//if(marker.mEditMode){
		//	var pos = marker.getPosition();
		//	QtWidget.marker_save(marker.mIdx, marker.mLocationId, pos.lat(), pos.lng());
		//	marker.setDraggable(false);
		//}
		//var ico = edit_mode ? icons.red : icons.yellow;
		//#marker.setIcon( new google.maps.MarkerImage(ico) );
		
		QtWidget.marker_clicked(marker.mWidget, marker.mId);
	});

	google.maps.event.addListener(marker, 'rightclick', function() {
		if(curr_idx > 0){
			markers[curr_idx].setIcon(markers[curr_idx].mIco);
			QtWidget.marker_unselected(curr_idx, markers[curr_idx].mLocationId);
		}
		curr_idx = marker.mIdx;
		marker.setIcon(icons.yellow); 
		QtWidget.marker_right_clicked(marker.mIdx, marker.mLocationId);
	});

	google.maps.event.addListener(marker, 'dblclick', function() {
		QtWidget.marker_double_clicked(marker.mIdx, marker.mLocationId);
	});

}

//*****************************************
//** select_marker_by_mid()
//*****************************************
function select_marker_by_mid(widget_name, myId, to_edit_mode){
	var emode = to_edit_mode > 0;
	marker = markers[widget_name][myId]
	curr_mid = myId;
	var miy = new google.maps.MarkerImage(icons.yellow);
	marker.setIcon(miy);
	marker.setDraggable(emode);
	marker.mEditMode = emode;
	z++;
	marker.setZIndex(z);
}

//*****************************************
//** set_marker_icon()
//*****************************************
function set_marker_icon(widget_name, myId, icon_color){
	marker = markers[widget_name][myId]
	if(!marker){
		return;
	}	
	var ico = icons[icon_color];
	if(!ico){
		QtWidget.map_error("No icon: " + icon_color);
	}
	var miy = new google.maps.MarkerImage(ico);
	marker.setIcon(miy);
	//marker.setDraggable(emode);
	//marker.mEditMode = emode;
	//z++;
	//marker.setZIndex(z);
}

//*****************************************
//** add_address_marker()
//*****************************************
function add_address_marker(location_id, label, lat, lng, lbl_method){
	if(init_flag == false){
		return false;
	}
	if(lbl_method == 'lookup'){
		var ico = icons.orange;
	}else{
		var ico = icons.green;
	}
	//alert("ere");
	var latlng = new google.maps.LatLng(lat, lng);
	markers[idx] = new google.maps.Marker({
								position: latlng, 
								map: map,
								icon: new google.maps.MarkerImage(ico),
								title: label,
								mLocationId: location_id,
								mIdx: idx,
								mIco: ico,
								mEditMode: false,
								draggable: true
	});	
	attach_marker(markers[idx], idx, label);
	QtWidget.marker_added(idx, location_id);
	idx++;
	return idx - 1; // return new id we just incremented
}

//*****************************************
//** add_marker()
//*****************************************
function add_marker(widget_name, myId, lat, lng, icon_color, label){
	if(init_flag == false){
		alert("never");
	}
	idx++;
	//alert(widget_name);
	//(markers[widget_name]);
	if( !markers[widget_name]){
		markers[widget_name] = {};
	}
	
	var ico = icons.purple;
	var latlng = new google.maps.LatLng(lat, lng);
	markers[widget_name][myId] = new google.maps.Marker({
								position: latlng, 
								map: map,
								icon: new google.maps.MarkerImage(icons[icon_color]),
								title: label,
								draggable: true,
								mId: myId,
								mWidget: widget_name,
								mIco: ico,
								mEditMode: false
	});
	attach_marker(markers[widget_name][myId], myId, label);
	QtWidget.marker_added(widget_name, myId);
	return idx; // pretty pointless
	
}

//** Clear Markers
function clear_markers(widget_name){
	if(!markers[widget_name]){
		return;
	}
	for(var myId in markers[widget_name]){
		markers[widget_name][myId].setMap(null);
	}
}

//** Hide/Show Markers
function hide_markers(widget_name, str_state){
	if(!markers[widget_name]){
		return;
	}
	var state = str_state == "1";
	for(var myId in markers[widget_name]){
		markers[widget_name][myId].setVisible(state)
	}
}

//***************************************
//** Place Marker
//***************************************
function placeMarker(location){
	if(!edit_mode){
		return;
	}
	var clickedLocation = new google.maps.LatLng(location);
	markers[idx] = new google.maps.Marker({
		position: location, 
		map: map,
		icon: icons.orange,
		mIdx: idx
	});
	QtWidget.marker_added(idx, location.lat(), location.lng());
	attach_marker(markers[idx], idx);
	idx++;
}

function map_ready(){
	return init_flag;
}

//***=======================================================================================================
//** Get Code for address
//***=======================================================================================================
function do_lookup(widget_name, location_id, search_text){
	//alert(address);
	//search_text = search_text + " UK";
	//#alert(search_text);
	if (geocoder) {
		geocoder.geocode({ 
			'address': search_text, country: '.uk'
			}, 
			function (results, status) {
				//alert(status);
				//*** Load Map ****
				if (status == google.maps.GeocoderStatus.OK) {
					
					//** send the return count (we cant return an "object".. yet,.. maybe json but decode issue
					QtWidget.lookup_result_count(widget_name, location_id, results.length);

					//* iterate the results and send indiv
					for(var r in results){
						var rec = results[r];

						var addr = rec.formatted_address;
						var lat = rec.geometry.location.lat();
						var lng = rec.geometry.location.lng();
						
						QtWidget.lookup_result_item( widget_name, location_id, addr, lat, lng);
					}					
				//*** Error ****
				} else {
					if(status == "ZERO_RESULTS"){
						//#//QtWidget.lookup_result_count(widget_name, location_id, results.length);
						QtWidget.lookup_result_count(widget_name, location_id, 0);
					}else{
						alert("Geocode was not successful for the following reason: " + status);
					}
				}
			}
		);
	}
}




function send_position(latlng){
	alert(latlng);
	QtWidget.mouse_move(latlng.lat(), latlng.lng());
	alert("pos");
}

//**==========================================================================
//** Initialize Map
//**==========================================================================
function initialize_map(){
	//debugTxt = document.getElementById("debug");
	mapDiv = document.getElementById("map_canvas");

	geocoder = new google.maps.Geocoder();
	var latlng = new google.maps.LatLng(52.55,-2.47);
	var mapOptions = {
		zoom: 8,
		center: latlng,
		mapTypeId: google.maps.MapTypeId.HYBRID,
		mapTypeControl: false,
		scaleControl: true
	};
	map = new google.maps.Map(mapDiv, mapOptions);

	//* MouseMove
	google.maps.event.addListener(map, 'mousemove', function(ev){
		QtWidget.map_mouse_move(ev.latLng.lat(), ev.latLng.lng());
	});

	//* RightClick
	google.maps.event.addListener(map, 'rightclick', function(ev){
		QtWidget.map_right_click(ev.latLng.lat(), ev.latLng.lng());
	});

	//* Zoom Changed
	google.maps.event.addListener(map, 'zoom_changed', function(ev){
		QtWidget.map_zoom_changed(map.getZoom());
	});

	//* Click Add Marker
	google.maps.event.addListener(map, 'dblclick', function(event){
		placeMarker(event.latLng);
	});

	//* sets default view
	set_default_view();
	/*
	var foo = [];
	for(var i in icons){
		img = new Image();
		img.src= icons[i];
		foo.push(img);
	}
	*/
	init_flag = true;
	QtWidget.set_map_init();
}

//*************************************************
//** Map Settings
//*************************************************

//## set_zoom
function set_zoom(zoom_level){
	map.setZoom(zoom_level);
}

//## Zoom to
function zoom_to(lat, lng, zoom_level){
	var latlng = new google.maps.LatLng(lat, lng);
	map.panTo(latlng);
	map.setZoom(zoom_level);
}
//## Zoom to Marker
function zoom_to_marker(widget_name, myId, zoom_level){
	var marker = markers[widget_name][myId];
	if(marker){
		map.setZoom(zoom_level);
		var latlng = marker.getPosition();
		map.panTo(latlng);
		
	}else{
		QtWidget.map_error("Marker not found");
	}
}
//## pan_to
function pan_to(lat, lng){
	var latlng = new google.maps.LatLng(lat, lng);
	map.panTo(latlng);
}

//## set_map_type
function set_map_type(map_type){
	map.setMapTypeId(map_type);
}

//## set_edit_mode
function set_edit_mode(em){
	edit_mode = em == 1 ? true : false;
	//alert(em)
	if(edit_mode){
		var newOptions = {draggableCursor: "crosshair"};
	}else{
		var newOptions = {draggableCursor: "default"};
	}
	map.setOptions(newOptions);
	//alert(newOptions);
}

//## set_default_view
function set_default_view(){
	map.setZoom(6);
	map.panTo(  new google.maps.LatLng(53.89, -3.01) );
}

function current_view(){
	var dic = {	zoom: map.getZoom(), 
				lat: map.getCenter().lat(), lng: map.genCenter().lng()
	};
	return dic;
}
