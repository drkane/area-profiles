
// create the area boundary based on the geojson object
var bounds = L.geoJSON(boundary_geo).getBounds();

// create the map
var map = L.map('map', { maxBounds: bounds, zoomSnap: 0.1, zoomControl: false });
map.setMinZoom(map.getBoundsZoom(map.options.maxBounds));

// add the base tile layer
var tileurl = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=' + access_token;
L.tileLayer(tileurl, {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    id: 'mapbox.light'
}).addTo(map);

// create a pane for the boundary layer
map.createPane('boundaryfill');
map.getPane('boundaryfill').style.zIndex = 450;
map.getPane('boundaryfill').style.pointerEvents = 'none';

// add the inverted boundary layer
var boundary = L.geoJSON(boundary_geo, {
    invert: true,
    renderer: L.svg({
        padding: 1 ,
        pane: 'boundaryfill',
    }),
    pane: 'boundaryfill',
    style: {
        "color": "#000",
        "weight": 1,
        "opacity": 1,
        "stroke": true,
        "fill": true,
        "fillColor": "#fff",
        "fillOpacity": 1,
    }
});

// add the boundary layer at the top
map.addLayer(boundary);
map.setMaxBounds(bounds);
map.fitBounds(bounds);

boundary.layer_id = 'boundary';

// make sure it always stays on top
map.on("overlayadd", function (event) {
    boundary.remove();
    boundary.addTo(map);
});

// set styles for the boundaries
var bound_styles = {
    "fill": false,
    "color": "#555",
    "weight": 0.5,
    "opacity": 0.5,
};

// put together layers into the control - start with boundaries
var overlays = {
    "Boundaries": {
        "No boundaries": L.geoJSON().addTo(map),
        "LSOA": L.geoJSON(boundary_lsoa_geo, { style: bound_styles }),
        "Wards": L.geoJSON(boundary_ward_geo, { style: bound_styles }),
    }
}

// put together layers of markers
if (markers && (Object.keys(markers).length > 0)){
    overlays["Markers"] = {
        "No markers": L.geoJSON().addTo(map),
    };
    var add_first = true;
    for(const i in markers){
        var markerLayer = L.markerClusterGroup().addLayers(
            Object.values(markers[i]).map(o => L.marker([o['lat'], o['long']]).bindPopup(o['name']))
        );
        if(add_first){
            markerLayer.addTo(map);
        }
        overlays["Markers"][i] = markerLayer;
        add_first = false;
    }
}

// add choropleth layers
if (lsoa_fill) {
    overlays["Show data"] = {};
    for (const i in lsoa_fill) {

        // function which works out the colour of a area
        var getDecileColour = function (value){
            var colours = [
                "#0864A7",
                "#0978C7",
                "#2690CC",
                "#4AADD2",
                "#7DCBD8",
                "#B0E1D6",
                "#D3EED5",
                "#E3F5D8",
                "#EFFCCA",
                "#FBFCB9",
            ]
            return colours[value];
        }

        // function that gets the style for a feature
        var layerStyle = function (feature) {
            var value = lsoa_fill[i]["data"][feature.properties.code] - 1;
            return {
                fillColor: getDecileColour(value),
                color: getDecileColour(value),
                fill: true,
                fillOpacity: 0.8,
                opacity: 0.8,
                stroke: false,
            };
        }

        // add the layers to the data
        if (lsoa_fill[i]["onByDefault"]){
            overlays["Show data"][i] = L.geoJSON(boundary_lsoa_geo, {style: layerStyle}).addTo(map);
        } else {
            overlays["Show data"][i] = L.geoJSON(boundary_lsoa_geo, { style: layerStyle });
        }
    }
}

// add the layer control
L.control.groupedLayers({}, overlays, {
    exclusiveGroups: ["Markers", "Boundaries", "Show data"],
    collapsed: false,
    hideSingleBase: true,
}).addTo(map);
