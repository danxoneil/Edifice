window.onload = init;

function init() {

//	Map for entire city - when ready, use clone() function to create inset map
	//var overview = new OpenLayers.Map('inset', {
//		maxExtent: new OpenLayers.Bounds(1173524.7058, 1898031.7821, 1178333.0059, 1902906.1645) 
//	});
//		maxResolution: auto,
//	    	maxExtent: new OpenLayers.Bounds(1091130.7724, 1813891.8902, 1205198.8501, 1951669.0201),
//		projection: new OpenLayers.Projection('EPSG:3435'),
//		units: 'ft',

	map = new OpenLayers.Map('map', {
		maxResolution: "auto",
		projection: new OpenLayers.Projection('EPSG:3435'),
		units: 'ft',
		numZoomLevels: 6,
		maxExtent: new OpenLayers.Bounds(-530651.654365917, 1084738.22396089, -525073.023945515, 1087586.75830336)
	});
			
	// Protocols - Retrieving GeoJSON files for vector layers
	// -----------------------------------------------------			
	var buildings_protocol = new OpenLayers.Protocol.HTTP({
		url: 'wicker_park_buildings.json',
		format: new OpenLayers.Format.GeoJSON({})
	});

	var roofs_protocol = new OpenLayers.Protocol.HTTP({
		url: 'wicker_park_roofs_new.json',
		format: new OpenLayers.Format.GeoJSON({})
	});

	var walls_protocol = new OpenLayers.Protocol.HTTP({
		url: 'wicker_park_walls_new.json',
		format: new OpenLayers.Format.GeoJSON({})
	});
	var streets_protocol = new OpenLayers.Protocol.HTTP({
		url: 'wicker_park_streets.json',
		format: new OpenLayers.Format.GeoJSON({})
	});


	var curbs_protocol = new OpenLayers.Protocol.HTTP({
		url: 'wicker_park_curbs.json',
	        format: new OpenLayers.Format.GeoJSON({})
	});

	// --------------------------------------------------
	// Layers
	// --------------------------------------------------

	var canvas = ['SVG', 'Canvas', 'VML'];

	buildings_layer = new OpenLayers.Layer.Vector('Buildings', {
		protocol: buildings_protocol,
		strategies: [new OpenLayers.Strategy.Fixed()],
		renderers: canvas,
		isBaseLayer: true
	});

	roofs_layer = new OpenLayers.Layer.Vector('Roofs', {
		protocol: roofs_protocol,
		strategies: [new OpenLayers.Strategy.Fixed()],
	});

	walls_layer = new OpenLayers.Layer.Vector('Walls', {
		protocol: walls_protocol,
		strategies: [new OpenLayers.Strategy.Fixed()],
	});

	streets_layer = new OpenLayers.Layer.Vector('Streets', {
		protocol: streets_protocol,
		strategies: [new OpenLayers.Strategy.BBOX()],
		renderers: canvas,
		isBaseLayer: false
	 });

	
	curbs_layer = new OpenLayers.Layer.Vector('Curbs', {
		protocol: curbs_protocol,
		renderers: canvas,
		strategies: [new OpenLayers.Strategy.BBOX()]
	});


	// --------------------------------------------------
	// Styles
	// --------------------------------------------------
	var buildings_style = new OpenLayers.Style({
		'fillColor': '#679e8b',
	    	'fillOpacity': .33,
	    	'strokeColor': '#000000',
	    	'strokeWidth': 2,
	});

	var buildings_style_map = new OpenLayers.StyleMap({
		'default': buildings_style
	});

	buildings_layer.styleMap = buildings_style_map;

	var roofs_style = new OpenLayers.Style({
		'fillColor': '#679e8b',
	    	'fillOpacity': .33,
	    	'strokeColor': '#000000',
	    	'strokeWidth': 2,
	});

	var roofs_style_map = new OpenLayers.StyleMap({
		'default': roofs_style
	});

	roofs_layer.styleMap = roofs_style_map;

	var walls_style = new OpenLayers.Style({
		'fillColor': '#679e8b',
	    	'fillOpacity': .33,
	    	'strokeColor': '#000000',
	    	'strokeWidth': 2,
	});

	var walls_style_map = new OpenLayers.StyleMap({
		'default': walls_style
	});

	walls_layer.styleMap = walls_style_map;
	var streets_style = new OpenLayers.Style({
		'strokeColor': '#616161',
	    	'strokeWidth': 3,
	});

	var streets_style_map = new OpenLayers.StyleMap({
		'default': streets_style
	});

	streets_layer.styleMap = streets_style_map;
			
	
	var curbs_style = new OpenLayers.Style({
		'strokeColor': '#616161',
	    	'strokeWidth': 0.5
	});

	var curbs_style_map = new OpenLayers.StyleMap({
		'default': curbs_style
	});

	curbs_layer.styleMap = curbs_style_map;


	//-----------------------------------------------------
	// Making Isometric
	// --------------------------------------------------
	//
// TODO: All the things	
// DONE: boom

	// ---------------------------------------------------------
	// Controls, Markers, and Mapmaking
	// ---------------------------------------------------------
	
	

	//map.addLayer(buildings_layer);

	map.addLayers([streets_layer, curbs_layer, buildings_layer, walls_layer, roofs_layer ]);


	// Overview Map
	
	// Top Panel - search, hood jump, log in
	// pretty certain by now this will NOT be made in OpenLayers
	
	// Layer Switcher - in this case layers will be things like hotspots
	// events, my friends, apts/homes, jobs, etc.
	
/*	var layerSwitcher = new OpenLayers.Control.LayerSwitcher({
		roundedCorner: true,
		roundedCornerColor: 'green'
	});

	map.addControl(layerSwitcher);
	*/

	var highlightCtrl = new OpenLayers.Control.SelectFeature(
			buildings_layer, {
				hover: true,
	    			highlightOnly: true,
	    			renderIntent: "temporary",
				});
	
	var bldg_select = new OpenLayers.Control.SelectFeature(
			 buildings_layer, {
				toggle: true,
	    			clickout: true
				});

	map.addControl(highlightCtrl);
	highlightCtrl.activate();
	map.addControl(bldg_select);
	bldg_select.activate();


// TODO: Get this working so that hovering over building only pops up name and address, clicking fills feature logs with bulk of data
// On second thought, seems to take too long
// Maybe just highlight only to give users visual clue of buildng they are about to select, then once they click it, display bulk data
//
// 	
	function displayPopup()  {
		$.getJSON('wicker_park_pretty.json', function(data) {
				var address = {
					'bldg_gid': data[i][0],
					'address': data[i]['bldgData']['address']
				};
		});
	}
			

	function bldg_selected(event) {
		var feature = event.feature;
		var bldg_gid = String(feature.attributes.bldg_gid);

		 $.getJSON('wicker_park_pretty.json', function(data) {
//			for ( var i = 0; i < data.length; i++) {
					//alert(data[bldg_gid]['bldgData']['address'])
//				if (feature.attributes.bldg_gid == data[bldg_gid]) {
		var popup = new OpenLayers.Popup.FramedCloud("popup",
				feature.geometry.getBounds().getCenterLonLat(),
				new OpenLayers.Size(200,100),
				"<h1>"+ data[bldg_gid]['bldgData']['address'] + "</h1>",
				null,
				true
				);

		feature.popup = popup;
		map.addPopup(popup);}
					
					//pup.innerHTML += data.features[i].properties.address ; }
				 
			);


	}


	function bldg_unselected(event) {
		map.removePopup(event.feature.popup);
		event.feature.popup.destroy();
		event.feature.popup = null;
	}




//		buildings_layer.events.register('featureselected', this, bldg_selected);
//		buildings_layer.events.register('featureunselected', this, bldg_unselected);
//
//
	buildings_layer.events.on({
		'featureselected': bldg_selected,
		'featureunselected': bldg_unselected
	});
		map.zoomTo(3);

	}
