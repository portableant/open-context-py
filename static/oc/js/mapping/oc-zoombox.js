L.Control.ZoomBox = L.Control.extend({
    _active: false,
    _map: null,
    includes: L.Mixin.Events,
    options: {
        position: 'topleft',
        className: 'fa fa-search-plus',
        modal: false
    },
    onAdd: function (map) {
        this._map = map;
        this._container = L.DomUtil.create('div', 'leaflet-zoom-box-control leaflet-bar');
        this._container.title = "Query a specific area";
        var link = L.DomUtil.create('a', this.options.className, this._container);
        link.href = "#";
        
        // Bind to the map's boxZoom handler
        var _origMouseUp = map.boxZoom._onMouseUp;
        map.boxZoom._onMouseUp = function(e){
            _origMouseUp.call(map.boxZoom, {
                clientX: e.clientX,
                clientY: e.clientY,
                which: 1,
                shiftKey: false
            });
            // get lat lng points from the map points
            var size = map.getSize();
            var container_point = new L.Point();
            container_point.x = e.layerX;
            container_point.y = e.layerY;
            //console.log(e);
            var box_point = map.containerPointToLatLng(container_point);
            if (typeof map.boxZoom.b_points !== 'undefined') {
                map.boxZoom.b_points.push(box_point);
            }
            else{
                map.boxZoom.b_points = [box_point];
            }
        };
        var _origMouseDown = map.boxZoom._onMouseDown;
        map.boxZoom._onMouseDown = function(e){
            _origMouseDown.call(map.boxZoom, {
                clientX: e.clientX,
                clientY: e.clientY,
                which: 1,
                shiftKey: true
            });
            // get lat lng points from the map points
            var size = map.getSize();
            var container_point = new L.Point();
            container_point.x = e.layerX;
            container_point.y = e.layerY;
            var box_point = map.containerPointToLatLng(container_point);
            if (typeof map.boxZoom.b_points !== 'undefined') {
                map.boxZoom.b_points.push(box_point);
            }
            else{
                map.boxZoom.b_points = [box_point];
            }
        };

        map.on('zoomend', function(){
            //console.log('X: ' + map.boxZoom.lastX + ' Y: ' + map.boxZoom.lastY);
            //console.log(map.boxZoom.b_points);
            if (typeof map.boxZoom.b_points !== 'undefined') {
                // console.log(map.boxZoom);
                var new_zoom = parseInt(map.geodeep) + map.getZoom();
                for (var i = 0, length = map.boxZoom.b_points.length; i < length; i++) {
                    var act_point = map.boxZoom.b_points[i];
                    act_point.lng = lon_oneeighty(act_point.lng);
                    if (i == 0) {
                        var min_lat = act_point.lat;
                        var min_lng = act_point.lng;
                        var max_lat = act_point.lat;
                        var max_lng = act_point.lng;
                    }
                    else{
                        if (act_point.lat < min_lat) {
                            min_lat = act_point.lat;
                        }
                        if (act_point.lng < min_lng) {
                            min_lng = act_point.lng;
                        }
                        if (act_point.lat > max_lat) {
                            max_lat = act_point.lat;
                        }
                        if (act_point.lng > max_lng) {
                            max_lng = act_point.lng;
                        }    
                    }
                }
                var distance = get_distance(min_lng, min_lat, max_lng, max_lat);
                console.log(distance);
                if (distance * 3.5 < new_zoom){
                    // hopefully better scaling when zoomed in
                    new_zoom = Math.round(distance * 3.5, 0);
                }
                var bbox_query = [min_lng, min_lat, max_lng, max_lat].join(',');
                if (map.getZoom() == map.getMaxZoom()){
                    L.DomUtil.addClass(link, 'leaflet-disabled');
                }
                else {
                    L.DomUtil.removeClass(link, 'leaflet-disabled');
                }
                var url = window.location.href;
                url = replaceURLparameter(url, 'geodeep', new_zoom);
                url = replaceURLparameter(url, 'disc-bbox', bbox_query);
                //console.log(url);
                map.show_region_loading();
                window.location = url; //load the page with the zoom query
            }
        }, this);
        if (!this.options.modal) {
            map.on('boxzoomend', this.deactivate, this);
        }

        L.DomEvent
            .on(this._container, 'dblclick', L.DomEvent.stop)
            .on(this._container, 'click', L.DomEvent.stop)
            .on(this._container, 'click', function(){
                this._active = !this._active;
                if (this._active && map.getZoom() != map.getMaxZoom()){
                    this.activate();
                }
                else {
                    this.deactivate();
                }
            }, this);
        return this._container;
    },
    activate: function() {
        L.DomUtil.addClass(this._container, 'active');
        this._map.dragging.disable();
        this._map.boxZoom.addHooks();
        L.DomUtil.addClass(this._map.getContainer(), 'leaflet-zoom-box-crosshair');
    },
    deactivate: function() {
        L.DomUtil.removeClass(this._container, 'active');
        this._map.dragging.enable();
        this._map.boxZoom.removeHooks();
        L.DomUtil.removeClass(this._map.getContainer(), 'leaflet-zoom-box-crosshair');
        this._active = false;
        this._map.boxZoom._moved = false; //to get past issue w/ Leaflet locking clicks when moved is true (https://github.com/Leaflet/Leaflet/issues/3026).
    }
});

L.control.zoomBox = function (options) {
  return new L.Control.ZoomBox(options);
};

function get_distance(xa, ya, xb, yb){
    var xpart = (xa - xb) * (xa - xb);
    var ypart = (ya - yb) * (ya - yb);
    var distance = Math.sqrt(xpart + ypart);
    return distance;
}

function lon_oneeighty(lon){
    if (lon > 180) {
        lon = lon - 360;
    }
    return lon;
}