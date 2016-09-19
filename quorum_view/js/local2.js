var agree_color = "white";
var missing_color = "rgb(36, 255, 36)";
var disagree_color = "rgb(255,109, 182)";
var map;
var overlay;
var all_nodes = [];


var global_paper = null;

function update_stats(update) {
    var stats = update.stats;
    //console.log(stats);
    
    // Sort degree by value
    var sortable = [];
    for (var node in stats.degree) {
        sortable.push([node, stats.degree[node]]);
    }
    sortable.sort(function(a,b) {return b[1] - a[1]});
    document.getElementById("num_nodes").innerHTML = "Number of nodes: " + stats.num_nodes;
    document.getElementById("last_ledger").innerHTML = "Ledger: " + stats.ledger;
};





 

/*
var drawNetworkNode = function(node_data,rad,map) {
    if (node_data.hasOwnProperty('lat')) {
        coords = {'lat': node_data.lat, 'lng': node_data.lon};
        var nodeCircle = new google.maps.Circle({
            strokeColor: '#ffffff',
            strokeWeight: 1.0,
            fillColor: '#ffffff',
            map: map,
            center: coords,
            radius: 800000
        });
    }
} */


function initMap() {
	map = new google.maps.Map(document.getElementById('map'), {
          center: {lat: 0, lng: 0},
          zoom:2,
          backgroundColor: 'hsla(0, 0%, 0%, 0)',
          disableDefaultUI: true
        });
	var styles =   [{"featureType":"all","elementType":"labels.text.fill","stylers":[{"saturation":36},{"color":"#000000"},{"lightness":40}]},{"featureType":"all","elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#000000"},{"lightness":16}]},{"featureType":"all","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#000000"},{"lightness":20}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#000000"},{"lightness":17},{"weight":1.2}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":20}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":21}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#000000"},{"lightness":17}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#000000"},{"lightness":29},{"weight":0.2}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":18}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":16}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":19}]},{"featureType":"water","elementType":"geometry","stylers":[{"color":"#000000"},{"lightness":10}]},
        {featureType: 'all',
            elementType: 'labels',
            stylers: [{visibility: 'off'}]
        }
	];
    map.setOptions({styles: styles});
}


window.onload = function() {

    function NodeMarker(node, inlinks, map, stat) {
            var coords = {'lat': node.lat, 'lng': node.lon};
            this.stroke_width = 2;
            this.data = node;
            this.coords = coords;
            this.map_ = map;
            this.radius_ = 4;
            this.width_ = 500;
            this.height_ = 500;
            this.div_ = null;
            this.stat = stat;
            try { 
                if(map) { 
                    this.setMap(map); 
                } 
            } catch(err) { 
                console.log("Here's the error: ");
                console.log(err.Message); 
            }
    }; 

    NodeMarker.prototype = new google.maps.OverlayView();

    NodeMarker.prototype.onAdd = function() {
            this.div_ = document.createElement('div');
            this.div_.style.borderStyle = 'none';
            this.div_.style.borderWidth = '0px';
            this.div_.style.position = 'absolute';
            var that = this;
            all_nodes.push(this);
            var paper = Raphael(this.div_, this.width_, this.height_);
            if (that.stat == 'agree') {
                var cir = paper.circle(this.radius_ + this.stroke_width,this.radius_ + this.stroke_width,this.radius_).attr({'stroke-width': this.stroke_width, 'stroke': agree_color, 'fill': 'rgba(255,255,255,0.0)'});
            }
            if (that.stat == 'missing') {
                var cir = paper.circle(this.radius_ + this.stroke_width,this.radius_ + this.stroke_width,this.radius_).attr({'stroke-width': this.stroke_width, 'stroke': missing_color, 'fill': 'rgba(255,255,255,0.0)'});
            }

            cir.mouseover(function() {
                var lineHeight = 12;
                var gap = 2;
                var gwidth = 25;
                var min_y = 12;
                var img = paper.image("img/rocket.png", 2*that.radius_ + 7, 5, gwidth, gwidth);
                img.node.setAttribute('class','highlight');
                var name = paper.text(gwidth + 2*that.radius_ + 15, min_y, "Node: " + that.data.id).attr({'text-anchor':'start','stroke':'white', 'fill': 'white','font-size': lineHeight + 'px', 'font-family': 'Courier'});
                name.node.setAttribute('class','highlight');
                var  pk = paper.text(gwidth + 2*that.radius_ + 15, min_y + lineHeight + gap, "Public Key: " + that.data.public_key).attr({'text-anchor':'start', 'stroke': 'white','fill':'white','font-size':lineHeight + 'px','font-family':'Courier'});
                pk.node.setAttribute('class', 'highlight');
                var  loc = paper.text(gwidth + 2*that.radius_ + 15 ,min_y + 2*(lineHeight + gap), "Location: " + that.data.loc).attr({'text-anchor':'start', 'stroke': 'white','fill':'white','font-size':lineHeight + 'px','font-family':'Courier'});
                loc.node.setAttribute('class', 'highlight');
                
                var thold = paper.text(gwidth + 2*that.radius_ + 15 ,min_y + 3*(lineHeight + gap), "Threshold: " + that.data.ledger.value.t).attr({'text-anchor':'start','stroke':'white', 'fill': 'white','font-size': lineHeight + 'px', 'font-family': 'Courier'});
                thold.node.setAttribute('class','highlight');

                var qslabel = paper.text(gwidth + 2*that.radius_ + 15 ,min_y + 4*(lineHeight + gap), "Quorum Set: ").attr({'text-anchor':'start','stroke':'white', 'fill': 'white','font-size': lineHeight + 'px', 'font-family': 'Courier'});
                qslabel.node.setAttribute('class','highlight');

                for (var ii = 0; ii < that.data.ledger.value.v.length; ii++) {
                    var yloc = min_y + (ii + 4)*(lineHeight + gap);
                    var qset = paper.text(gwidth + 2*that.radius_ + 100 ,yloc, that.data.ledger.value.v[ii]).attr({'text-anchor':'start','stroke':'white', 'fill': 'white','font-size': lineHeight + 'px', 'font-family': 'Courier'});
                qset.node.setAttribute('class','highlight');
                }




                // Now do the path thing.  
                // Get all nodes
                var overlayProjection = that.getProjection();
                var rnode= all_nodes[Math.floor(Math.random()*all_nodes.length)];
                var ocoords = new google.maps.LatLng(that.coords.lat, that.coords.lng);
                var dcoords = new google.maps.LatLng(rnode.coords.lat, rnode.coords.lng);
                var orig = overlayProjection.fromLatLngToDivPixel(ocoords);
                var dest = overlayProjection.fromLatLngToDivPixel(dcoords);
                console.log(dest);
                var path_string = 'M ' + orig.x + ',' + orig.y + ' L ' + dest.x + ',' + dest.y;
                console.log(path_string);
                console.log(global_paper);
                var path = global_paper.path(path_string).toFront();
                path.attr('stroke', 'white');
                path.node.setAttribute('class', 'laser');


            });

            cir.mouseout(function() {
                var els = document.getElementsByClassName("highlight");
                while (els.length > 0) {
                    els[0].parentNode.removeChild(els[0]);
                }
                var els = document.getElementsByClassName("laser");
                while (els.length > 0) {
                    els[0].parentNode.removeChild(els[0]);
                }
            });

            var panes = this.getPanes();
            panes.overlayMouseTarget.appendChild(this.div_);
    }

    NodeMarker.prototype.draw = function() {
            global_paper = Raphael('map',1000,1000);
            global_paper.node.setAttribute('z-index', 1000);
            var circ = global_paper.circle(100,200,200).attr({'stroke': 'white'}).toFront();
            var overlayProjection = this.getProjection();
            var gcoords = new google.maps.LatLng(this.coords.lat, this.coords.lng);         //Lame! Google!
            var o = overlayProjection.fromLatLngToDivPixel(gcoords);
            var l = o.x - this.radius_ - 2*this.stroke_width;
            var t = o.y - this.radius_ - 2*this.stroke_width;
            this.div_.style.left = l + 'px';
            this.div_.style.top = t + 'px';
    }

    function ws_onmessage(e) {

        update_stats(JSON.parse(e.data));
        // emove the old nodes
        var olds = document.getElementsByTagName('svg');
        for (ii of olds) {
            ii.remove();
        }
        var d = JSON.parse(e.data);

        var get_id_number_from_name = function(name) {
            for (var ii = 0; ii < d.agree.nodes.length; ii++) {
                if (d.agree.nodes[ii].id === name) {
                    return ii;
                }
            }
            return null;
        }

    function count_in_links(name) {
      var id_number = get_id_number_from_name(name);
        var in_links = 0;
        for (var ii in d.agree.links) {
          if (d.agree.links[ii].target === id_number) {
              in_links += 1;
          }
        }
        return in_links;
    }



        for (var ii = 0; ii < d.agree.nodes.length; ii++) {
            if (d.agree.nodes[ii].hasOwnProperty('lat')) {	
                    var inlinks = count_in_links(d.agree.nodes[ii].id);
                    var overlay = new NodeMarker(d.agree.nodes[ii], inlinks, map, 'agree');
            }
        }

        for (var ii = 0; ii < d.missing.nodes.length; ii++) {
            if (d.missing.nodes[ii].hasOwnProperty('lat')) {	
                    var inlinks = count_in_links(d.missing.nodes[ii].id);
                    var overlay = new NodeMarker(d.missing.nodes[ii], inlinks, map, 'agree');
            }
        }


    }

    var ws = new WebSocket("ws://stellar.network:1011/update/ws");
    ws.onmessage = ws_onmessage;

}

