
// optimized version for threshold rendering
function CanvasTileLayerThreshold (canvas_setup, filter) {
    CanvasTileLayer.call(this, canvas_setup, filter);
    this.maxval = 100;
    this.minval = 25;
}

CanvasTileLayerThreshold.prototype = new CanvasTileLayer();

CanvasTileLayerThreshold.prototype.filter_tiles = function() {
    var new_min = arguments[0];
    var new_max = arguments[1];
    CanvasTileLayer.prototype.filter_tiles.apply(this, arguments)
    this.minval = new_min;
    this.maxval = new_max;
}

CanvasTileLayerThreshold.prototype.filter_tile = function(canvas, args) {
    var new_min = args[0];
    var new_max = args[1];
    var ctx = canvas.getContext('2d');
    if(new_min < this.minval) {
        //console.log("rendering");
        ctx.drawImage(canvas.image, 0, 0);  
    }
    var I = ctx.getImageData(0, 0, canvas.width, canvas.height);
    this.filter.apply(this, [I.data, ctx.width, ctx.height].concat(args));
    ctx.putImageData(I,0,0);
}

var App = function() {
        var me = {
            mapOptions: {
                zoom: 4,
                center: new google.maps.LatLng(43, -76),
                mapTypeId: google.maps.MapTypeId.ROADMAP
            }
        };

        function filter(image_data, w, h, minval, maxval) {
            console.log(minval);
            var components = 4; //rgba
            var pixel_pos;
            maxval = maxval+10;
            minval = minval-10;
            for(var i=0; i < w; ++i) {
                for(var j=0; j < h; ++j) {
                    var pixel_pos = (j*w + i) * components;
                    if(255-image_data[pixel_pos] < minval || maxval < 255-image_data[pixel_pos]) {
                        image_data[pixel_pos] = image_data[pixel_pos + 1] = image_data[pixel_pos + 2] = 0;
                        image_data[pixel_pos + 3] = 0;
                    } else {
                        image_data[pixel_pos] = 255;
                        image_data[pixel_pos + 1] = image_data[pixel_pos + 2] = 0;
                        image_data[pixel_pos + 3] = 255-(.25*image_data[pixel_pos]);
                    } 
                }
            }
        };

        function canvas_setup(canvas, coord, zoom) {
          var image = new Image();  
          var ctx = canvas.getContext('2d');
          //image.src = "/proxy/mountainbiodiversity.org/env/z" + zoom + "/"+ coord.x + "/" + coord.y +".png";
          image.crossOrigin='';
          image.src = "http://ec2-46-137-148-168.eu-west-1.compute.amazonaws.com/ArcGIS/rest/services/ecohack/bio13_13/MapServer/tile/" + zoom + "/"+ coord.y + "/" + coord.x +".png";
          canvas.image = image;
          $(image).load(function() { 
                //ctx.globalAlpha = 0.5;
                ctx.drawImage(image, 0, 0);  
                App.heightLayer.filter_tile(canvas, [App.minval, App.maxval]);
          });
        }

        me.init = function(id, layer) {
            this.layer = layer;
            var map = new google.maps.Map(document.getElementById(id), this.mapOptions);
            
        	var map_style = [
              {
                elementType: "geometry",
                stylers: [
                  { saturation: -6 },
                  { lightness: 94 }
                ]
              },{
                elementType: "labels",
                stylers: [
                  { visibility: "off" }
                ]
              },{
                featureType: "water",
                stylers: [
                  { saturation: 7 },
                  { lightness: -100 },
                  { gamma: 0.62 }
                ]
              },{
                featureType: "administrative.country",
                stylers: [
                  { lightness: -100 },
                  { gamma: 0.9 },
                  { visibility: "simplified" }
                ]
              },{
              }
            ]

        	map.setOptions({styles: map_style});
	
            this.map = map;
            this.minval = 0;
            this.maxval = 0;
        }
        me.draw = function(minval,maxval) {
            this.minval = minval;
            this.maxval = maxval;
            this.heightLayer = this.layer || new CanvasTileLayerThreshold(canvas_setup, filter);
            this.map.overlayMapTypes.insertAt(0, this.heightLayer);
        }
        return me;
    }();


