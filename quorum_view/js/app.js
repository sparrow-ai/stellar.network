var agree_color = "white";
var missing_color = "rgb(36, 255, 36)";
var disagree_color = "rgb(255,109, 182)";

var svg;

var radius = 6;
var width = window.innerWidth || document.body.clientWidth;
var width = width*1.0;
var height = window.innerHeight || document.body.clientHeight;
var height = height*1.0;
var radius = 6;
var max_rad = 41;



function update_stats(update) {
    var stats = update.stats;
    //console.log(stats);
    
    // Sort degree by value
    var sortable = [];
    for (var node in stats.degree) {
        sortable.push([node, stats.degree[node]]);
    }
    sortable.sort(function(a,b) {return b[1] - a[1]});


    document.getElementById("node_degrees").innerHTML = "<span>Node degrees:</span>";
    var list = document.createElement("ul"); 
    for (var ii in sortable) {
        var the_name = sortable[ii][0];
        if (the_name.length > 50) {
            the_name = the_name.substring(0,6);
        }
        var item = document.createElement('li');
        var span = document.createElement('div');
        span.setAttribute("style", "width: 30px; display: inline;");
        span.appendChild(document.createTextNode(the_name + ": "));
        item.appendChild(span);
        item.appendChild(document.createTextNode(sortable[ii][1]));
        list.appendChild(item);
        
    }
    document.getElementById("node_degrees").appendChild(list); 


    document.getElementById("num_nodes").innerHTML = "Number of nodes: " + stats.num_nodes;
    document.getElementById("last_ledger").innerHTML = "Ledger: " + stats.ledger;

};

function update_network_from_json(update) {
    var width = window.innerWidth || document.body.clientWidth;
    var width = width*1.0;
    var height = window.innerHeight || document.body.clientHeight;
    var height = height*1.0;
    var radius = 6;

    var graph = update.agree;
    var missing = update.missing;
    var disagree = update.disagree;

    function get_id_number_from_name(name) {
        for (var ii = 0; ii < graph.nodes.length; ii++) {
            if (graph.nodes[ii].id === name) {
                return ii;
            }
        }
        return null;
    }

    function get_node_from_update(name) {
        for (var ii = 0; ii < graph.nodes.length; ii++) {
            if (graph.nodes[ii].id === name) {
                return graph.nodes[ii];
            }
        }
        return null;
    }

  function count_in_links(name) {
      var id_number = get_id_number_from_name(name);
        var in_links = 0;
        for (var ii in graph.links) {
          if (graph.links[ii].target === id_number) {
              in_links += 1;
          }
        }
        return in_links;
  }

    var nodes = d3.selectAll(".node");

    for (var ii = 0; ii < nodes[0].length; ii++) {

        var name = nodes[0][ii].childNodes[1].innerHTML;
        var new_node = get_node_from_update(name);
        if (new_node === null) { //Is not null
            // This node existed before.  Check the color and size.
            if (!new_node.hasOwnProperty("ledger")) {
               nodes[0][ii].childNodes[0].setAttribute('stroke', missing_color);
            } else if (new_node.hasOwnProperty("ledger")) { 
                if (!new_node.ledger) {
                    nodes[0][ii].childNodes[0].setAttribute('stroke', missing_color);
                } else if (new_node.ledger.missing == 1) {
                    nodes[0][ii].childNodes[0].setAttribute('stroke', missing_color);
                } else if (new_node.ledger.disagree ==1) {
                    nodes[0][ii].childNodes[0].setAttribute('stroke', disagree_color);
                    return "#bd1550";
                } else {

                    nodes[0][ii].childNodes[0].setAttribute('stroke', "white");
                }
            } else {
                nodes[0][ii].childNodes[0].setAttribute('stroke', "white");
            }


            // Now check size
           var inlinks = count_in_links(name);
           //console.log('inlinks: '+inlinks);
           nodes[0][ii].childNodes[0].setAttribute('r',1 + 2*inlinks);
           nodes[0][ii].childNodes[0].setAttribute('stroke-width',1 + 0.5*inlinks);
        }
    }
}

function draw_network(filename, nav_el, description) {
    document.getElementById("graph").innerHTML = "";

    var width = window.innerWidth || document.body.clientWidth;
    var width = width*0.8;
    var height = window.innerHeight || document.body.clientHeight;
    var height = height*0.8;
    var radius = 6;

    d3.select("#network").remove();

    d3.json(filename, function(error, graph) {
    if (error) throw error;
    d3.json("networkdata/missing.json",function(error,missing) {
        if (error) throw error;

    d3.json("networkdata/disagree.json",function(error,disagree) {
        missing_links = missing['links'];

    var force = d3.layout.force()
                         .size([width, height])
                         .charge(-500)
                         .gravity(0.1)
                         .linkDistance(150)
			 .on("tick", tick);

  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();

    var svg = d3.select("#graph").append("svg").attr("width", width).attr("height", height).attr("id","network");


  var path = svg.append("svg:g").selectAll("path")
      .data(force.links())
      .enter().append("svg:path")
      .attr("class", "link")
      .attr("marker-end", "url(#end)")
      .style("stroke","white")
      .style("fill-opacity", 0.0)
      .style("stroke-width",0.3);

    svg.append("svg:defs").selectAll("marker")
    .data(["end"])      // Different link/path types can be defined here
    .enter().append("svg:marker")    // This section adds in the arrows
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX",15) 
    .attr("refY", -1.5)
    .attr("markerWidth", 8)
    .attr("markerHeight", 8)
    .attr("orient", "auto")
    .append("svg:path")
    .attr("d", "M0 -5 L 10 0 L 0 5")
    .style("stroke", "white")
    .style("stroke-width",1.0)
    .style("fill", "white");




  var node = svg.selectAll(".node")
      .data(force.nodes())
      .enter().append("g")
      .attr("class", "node")
      .style("fill", function(d) {
          return "#ffdddd"; 
      })
      .call(force.drag);

  function count_in_links(name) {
      var in_links = 0;
      for (var ii in graph.links) {
          if (graph.links[ii].target.id == name.id) {
              in_links += 1;
          }
      }
      return in_links;
  }

  node.append("circle")
      .attr('r', function(d) {
          return 1+2*count_in_links(d)})
      .attr('fill', 'white')
      .attr('fill-opacity', 0)
      .attr('stroke',function(d) {
        if (!d.hasOwnProperty("ledger")) {
           return missing_color;
        } else if (d.hasOwnProperty("ledger")) { 
            if (!d.ledger) {
                return missing_color;
            } else if (d.ledger.missing == 1) {
                return missing_color;
            } else if (d.ledger.disagree ==1) {
                return disagree_color;
            }
        } else {
            return "white";
        }
      })
      .attr('stroke-width', function(d) {
          return 1 + 0.5*count_in_links(d);
      }).on('mouseover', function(d) {
            var all_select = d3.selectAll("svg").selectAll('.node').attr("opacity", function(de) {
                var this_id = d3.select(this).select('text').text();
                return (de.id == d.id) ? 1.0 : 0.2;
            });
            d3.selectAll("svg").selectAll('path').attr('opacity', 0.2);
            var mult = 1.5;
            var mydx = 2;
            var the_g = d3.select(this.parentNode)
              .append('g')
              .attr('class','highlighted')
              .append('text')
              .attr('class','qset_label')
              .attr('fill', 'white')
              .attr('dx', mydx + 'em') 
              .attr('dy',1.5*mult + 'em')
              .text(function(d) {
                  return 'Node ID:    ' + d.public_key;
              });

            d3.select(this.parentNode)
              .append('text')
              .attr('class','qset_label')
              .attr('fill', 'white')
              .attr('dx', mydx + 'em') 
              .attr('dy',2.5*mult + 'em')
              .text(function(d) {
                  if (d.hasOwnProperty('loc')) {

                    return 'Version:  ' + d.version;
                  } else {
                      return "";
                  }
              });

        

            var the_g = d3.select(this.parentNode)
              .append('text')
              .attr('class','qset_label')
              .attr('fill', 'white')
              .attr('dx', mydx + 'em') 
              .attr('dy',3.5*mult + 'em')
              .text(function(d) {
                  if (d.hasOwnProperty('loc')) {

                    return 'Location:  ' + d.loc;
                  } else {
                      return "";
                  }
              });
            
            if (d.ledger != null) {
                var thold = d.ledger.value.t;
                var qset = d.ledger.value.v;
                d3.select('.qset_data').remove();
                var this_select = d3.select('.highlighted')
                     .append('text')
                     .attr('class','qset_label')
                     .attr('dx',mydx + 'em')
                     .attr('dy', 4.5*mult + 'em')
                     .attr('fill','white')
                     .text('Threshold:  ' + thold);

                var this_select = d3.select('.highlighted')
                     .append('text')
                     .attr('class','qset_label')
                     .attr('dx',mydx + 'em')
                     .attr('dy', 5.5*mult + 'em')
                     .attr('fill','white')
                     .text('Quorum set: ');

                var this_select = d3.select('.highlighted').selectAll('.qset_data');
                this_select
                  .data(qset)
                  .enter()
                  .append('text')
                  .attr('class','qset_data')
                  .attr('dx', '9em')
                  .attr('font-family','Courier')
                  .attr('dy', function(d,i) {return 5.5*mult + i*mult + 'em';})
                  .attr('fill', 'white')
                  .text(function (d) {
                      return d;
                  });
                }
    })
      .on('mouseout', function(d) {
            d3.selectAll("svg").selectAll('.node').attr("opacity", function(de) {
                return 1.0;
            });
            d3.selectAll("svg").selectAll('path').attr('opacity', 1.0);

          d3.select(this.parentNode).selectAll('.highlighted').remove();
          d3.select(this.parentNode).selectAll('.info').remove();
          d3.select(this.parentNode).selectAll('.qset_label').remove();
          d3.select(this.parentNode).selectAll('.qset_data').remove();
      });

  node.append("text")
      .attr("dx", function (d) {
          var in_links = count_in_links(d);
          return 0.2 + 0.2*in_links + 'em';
      })
      .attr("dy", ".35em")
      .attr("fill", "white")
      .text(function(d) {
          if (d.id.length > 50) {
            return '@' + d.id.substring(0,5)
          } else {
             return d.id
          }
      });

/*  node.append('text')
      .attr("dx",'1em')
      .attr("dy", "1.8em")
      .attr("fill", "white")
      .text('Quorum set: ')
      .style("visibility", "hidden");

 */ 

/*
      .append("forignObject")
      .attr('width', 200)
      .attr('height', 200)
      .append('xhtml:div')
      .append('div')
      .html(function(d) {
          console.log(d);
          if (!!d.ledger) {
            return 'Quorum set: ' + d.ledger.value.v;
          } else {
              return null;
          }
      })
      .style("visibility", "hidden");
*/

  /*
          if (!!d.ledger) {
            return '<tspan>Quorum set: </tspan>' + d.ledger.value.v;
          } else {
              return null;
          }
      }).style("visibility","hidden");  */

  //var desc = node.append('desc');
  //desc.html(function(d) {return "Hi!";});


  //node.append("title")
  //    .text(function(d) { return d.id; });

  function tick() {
	path.attr("d", function(d) {
        return "M" + 
            Math.max(max_rad,Math.min(width - max_rad,d.source.x)) + "," + 
            Math.max(max_rad,Math.min(height - max_rad,d.source.y)) + "L" + 
            Math.max(max_rad,Math.min(width- max_rad,d.target.x)) + "," + 
            Math.max(max_rad,Math.min(height- max_rad,d.target.y));
            /*d.source.x + "," + 
            d.source.y + "L" + 
            d.target.x + "," + 
            d.target.y; */
    })
    //.attr("cx", function(d) { return d.source.x = Math.max(radius,Math.min(width - radius,d.source.x)); })
    .attr("cx", function(d) { return d.x = Math.max(max_rad,Math.min(width - max_rad,d.x)); })
    //.attr("cy", function(d) { return d.source.y = Math.max(radius,Math.min(height- radius,d.source.y)); });
    .attr("cy", function(d) { return d.y = Math.max(max_rad,Math.min(height- max_rad,d.y)); });
        
    node.attr("transform", function(d) { return "translate(" + Math.max(max_rad, Math.min(width-max_rad,d.x)) + "," + Math.max(max_rad, Math.min(height-max_rad, d.y))+ ")"; }); 
    }

    });

    });
    });

    return svg;
}



function network_stats(filename) {
    d3.json(filename, function(error, stats) {
    if (error) throw error;

    // Sort degree by value
    var sortable = [];
    for (var node in stats.degree) {
        sortable.push([node, stats.degree[node]]);
    }
    sortable.sort(function(a,b) {return b[1] - a[1]});


    document.getElementById("node_degrees").innerHTML = "<span>Node degrees:</span>";
    var list = document.createElement("ul"); 
    for (var ii in sortable) {
        var the_name = sortable[ii][0];
        if (the_name.length > 50) {
            the_name = the_name.substring(0,6);
        }
        var item = document.createElement('li');
        var span = document.createElement('div');
        span.setAttribute("style", "width: 30px; display: inline;");
        span.appendChild(document.createTextNode(the_name + ": "));
        item.appendChild(span);
        item.appendChild(document.createTextNode(sortable[ii][1]));
        list.appendChild(item);
        
    }
    document.getElementById("node_degrees").appendChild(list); 



    document.getElementById("num_nodes").innerHTML = "Number of nodes: " + stats.num_nodes;
    document.getElementById("last_ledger").innerHTML = "Ledger: " + stats.ledger;

    });
};


function draw_background() {
    var width = window.innerWidth || document.body.clientWidth;
    var height = window.innerHeight || document.body.clientHeight;

    var svg = d3.select("body").append("svg").attr("width", width).attr("height", height).attr("id","background");

    var starGroup = svg.append("g")
                       .attr("class", "stars");

    var num_stars = 2000;
    var stars = [];
    for (var ii = 0; ii < num_stars; ii++) {
        var x = Math.random()*width;
        var y = Math.random()*height;
        var rad = Math.random();
        var color = d3.rgb(Math.floor(Math.random()*(255-150) + 150),
                     Math.floor(Math.random()*(255-150) + 150),
                     Math.floor(Math.random()*(255-150) + 150));

        stars.push({'x': x, 'y': y, 'r': rad, 'color': color});
    }

    var circles = starGroup.selectAll("circle")
                     .data(stars)
                     .enter()
                     .append("circle");

    var circleAttr = circles
                      .attr('cx', function(d) { return d.x = Math.max(rad, Math.min(width-rad, d.x));})
                      .attr('cy',function(d) { return d.y = Math.max(rad, Math.min(height - rad, d.y));})
                      .attr('r', function(d) { return d.r;})
                      .style('fill', color)
                      .style('opacity', function (d) {
                          return Math.random()*0.5;});
}

function ws_onmessage(e) {
    //console.log(JSON.parse(e.data)); 
    update_network_from_json(JSON.parse(e.data));
    update_stats(JSON.parse(e.data));
}

window.onload = function() {

    var ws = new WebSocket("ws://stellar.network/update/ws");
    ws.onmessage = ws_onmessage;
    //ws.send("This is a thing I send.");

    var agree_el = document.getElementById("nav-agree");
    //var disagree_el = document.getElementById("nav-disagree");
    //var missing_el = document.getElementById("nav-missing");
    //var fail_with_el = document.getElementById("nav-fail-with");
    var start = function(e) {
        desc = "Nodes represent validators in the consensus network.  The color of the node represents the node's status in the last observed ledger.  The radius of each node is increasing in the number of other nodes that rely on it for consensus.  Edges eminating from a node point toward the validators in that node's quorum set.";
        svg = draw_network('networkdata/agree.json', e, desc);
        network_stats('networkdata/agree_stats.json');
    }
    //disagree_el.onclick = function(e) {
    //    desc = "Edges connect nodes in the quorum set that disagreed on the last observed ledger";
    //    draw_network('networkdata/disagree.json', e, desc );
    //    network_stats('networkdata/disagree_stats.json');
    //}
    //missing_el.onclick = function(e) {
    //    desc = "Edges connect nodes in the quorum set that were missing for the last observed ledger";
    //    draw_network('networkdata/missing.json', e, desc);
    //    network_stats('networkdata/missing_stats.json');
    //}
    //fail_with_el.onclick = function(e) {
    //    desc = "Edges connect nodes in the quorum set that are connected through the 'Fail with' value";
    //    draw_network('networkdata/fail_with.json', e, desc);
    //    network_stats('networkdata/fail_with_stats.json');
    //}
    start();
    draw_background();

}
