




function NodeMarker(node, inlinks, map) {
        coords = {'lat': node.lat, 'lng': node.lon};
        this.inlinks = inlinks;
        this.coords = coords;
        this.map_ = map;
        this.width_ = 32;
        this.height_ = 32;
        this.div_ = null;
        this.setMap = map;
}


NodeMarker.prototype.onAdd = function() {
        var div = document.createElement('div');
        div.style.borderStyle = 'none';
        div.style.borderWidth = '0px';
        div.style.position = 'absolute';

        var paper = Raphael(div, this.width_, this.height_);
        var cir = paper.circle(0,0,100).attr({'stroke-width': 10, 'stroke': 'white'});
        
        var panes = this.getPanes();
        panes.overlayMouseTarget.appendChild(div);
}

NodeMarker.prototype.draw = function() {
        var overlayProjection = this.getProjection();
        var o = overlayProjection.fromLatLngToDivPixel(this.pos_);
        var l = o.x - Math.round(this.width_ / 2);
        var t = o.y - this.height_;

}

