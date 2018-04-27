---
layout: data
title:  "Air Quality"
date:   2018-03-04
categories: air_quality
---

<script src='https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.js'></script>
<link href='https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.css' rel='stylesheet' />

<div id='map' style='width: 100%; height: 500px;'></div>
<script>

mapboxgl.accessToken = '{{site.mapbox-token}}';

var map = new mapboxgl.Map({
   container: 'map', // container id
   style: 'mapbox://styles/mapbox/streets-v9', // style sheet location
   center: [-122.288356, 37.813146], // starting position, center of W Oakland
   zoom: 12 // starting zoom
});

map.on('load', function () {
    map.addLayer({
        "id": "points",
        "type": "circle",
        "source": {
            "type": "geojson",
            "data": {{site.data.test|jsonify}}
      }
   });
});
</script>
