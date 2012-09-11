window.onload = init()
	function init() {
		map = L.map('map', {
			center: [39.5255529375311, -93.6923186748782], // rotated and scaled centroid of neighborhood in lat/lon (EPSG; 4326)
			zoom: 4, // changing this doesn't seem to do anything, yet it must be specified
			maxBounds: new L.LatLngBounds(new L.LatLng(39.5212011611326, -93.7018623028632), new L.LatLng(39.5298975802579, -93.6827727836862))
		});

		var buildingsStyle = {
			'color': '#679e8b',
			'opacity': 1, // still looks transparent - guessing Leaflet has something that detects overlapping features
					// and automatically makes them transparent - could be a problem down the road
			'weight': 2
		};

		var streetsStyle = {
			'color': '#616161',
			'weight': 3
		};

		var curbsStyle = {
			'color': '#616161',
			'weight': 0.5
		};

		$.getJSON('wp_4326_buildings.json', function(data) {
			var buildings = new L.GeoJSON(data, { style: buildingsStyle });
			buildings.addTo(map);
		});
		$.getJSON('wp_4326_walls.json', function(data) {
			var walls = new L.GeoJSON(data, { style: buildingsStyle });
			walls.addTo(map);
		});
		$.getJSON('wp_4326_streets.json', function(data) {
			var streets = new L.GeoJSON(data, { style: buildingsStyle });
			streets.addTo(map);
		});
		$.getJSON('wp_4326_curbs.json', function(data) {
			var curbs = new L.GeoJSON(data, { style: buildingsStyle });
			curbs.addTo(map);
		});
	}
