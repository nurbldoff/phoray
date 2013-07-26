var view3d = (function () {

    var radians = Math.PI / 180;

    function setup_lights (scene) {
        var light = new THREE.DirectionalLight( 0xFFFFFF, 0.5 );
        light.position.set( 10, 0, 5 );
        light.lookAt( scene.position );
        scene.add( light );

        light = new THREE.DirectionalLight( 0xFFFFFF, 1.0 );
        light.position.set( -10, 10, 5 );
        light.lookAt( scene.position );
        scene.add( light );

        light = new THREE.DirectionalLight( 0xFFFFFF, 0.5 );
        light.position.set( 0, -10, -5 );
        light.lookAt( scene.position );
        scene.add( light );
    }

    function setup_grid (scene) {
        // Grid
        var size = 10, step = 1;
        var geometry = new THREE.Geometry();
        var material = new THREE.LineBasicMaterial( { vertexColors: THREE.VertexColors } );
        var color1 = new THREE.Color( 0x888888 ), color2 = new THREE.Color( 0x666666 );

        for ( var i = - size; i <= size; i += step ) {
	    geometry.vertices.push( new THREE.Vector3( -size, 0, i ) );
	    geometry.vertices.push( new THREE.Vector3(  size, 0, i ) );

	    geometry.vertices.push( new THREE.Vector3( i, 0, -size ) );
	    geometry.vertices.push( new THREE.Vector3( i, 0,  size ) );

	    var color = i === 0 ? color1 : color2;

	    geometry.colors.push( color, color, color, color );
        }
        var grid = new THREE.Line( geometry, material, THREE.LinePieces );
        scene.add(grid);
    }

    function setup_input(view, element) {

        element.onmousedown = function (event) {
            event.preventDefault();

	    view.mouse_start = {x: ( event.clientX / element.offsetWidth ) * 2 - 1,
	                        y: ( event.clientY / element.offsetHeight ) * 2 + 1};
            view.start_theta = view.theta;
            view.start_phi = view.phi;

            view.mouse_down = true;
        };

        element.onmouseup = element.onmouseout = function ( event ) {
            view.mouse_down = false;
        };

        element.onmousemove = function ( event ) {

	    event.preventDefault();

            if (view.mouse_down) {
	        view.mouse_pos = {x: ( event.clientX / element.offsetWidth ) * 2 - 1,
	                     y: ( event.clientY / element.offsetHeight ) * 2 + 1};
                view.render();
            }

        };
        // helper for mousewheel events
        function hookEvent(element, eventName, callback)
        {
            if(typeof(element) == "string")
                element = document.getElementById(element);
            if(element == null)
                return;
            if(element.addEventListener)
            {
                if(eventName == 'mousewheel')
                    element.addEventListener('DOMMouseScroll', callback, false);
                element.addEventListener(eventName, callback, false);
            }
            else if(element.attachEvent)
                element.attachEvent("on" + eventName, callback);
        }

        // attach callback for mousewheel zooming
        hookEvent(element, "mousewheel", function (event) {
            event = event ? event : window.event;
            var wheelData = event.detail ? event.detail : event.wheelDelta;
            if (wheelData > 0) {
                view.scale *= 1.1;
            } else {
                view.scale /= 1.1;
            }
            view.render();
        });
    }


    this.View = function (element) {
        this.traces = null;
        this.traces = new THREE.Object3D();

        if (!Detector.webgl) {
            var warning = Detector.getWebGLErrorMessage();
            document.getElementById('view').appendChild(warning);

            // It should be possible to run with the canvas renderer if the webgl
            // backend doesn't work. Needs testing and probably some tweaking, though.

        } else {
            this.renderer = new THREE.WebGLRenderer({antialias: true});
            this.renderer.autoClear = false;
            //this.renderer = new THREE.CanvasRenderer({antialias: false});

            var view_width = element.offsetWidth, view_height = element.offsetHeight;

            // Camera coodinates
            this.theta = -Math.PI / 4;
            this.start_theta = this.theta,
            this.phi = Math.PI / 6;
            this.start_phi = this.phi;
            this.mouse_start = {x: 0, y: 0};
            this.mouse_pos= {x: 0, y: 0};
            this.mouse_down = false;
            this.scale = 1;

            element.parentNode.replaceChild(this.renderer.domElement, element);
            element = this.renderer.domElement;
            element.id = "view";
            this.renderer.setSize( view_width, view_height );

            this.scene = new THREE.Scene();
            this.overlay = new THREE.Scene();
            this.camera = new THREE.OrthographicAspectCamera(
                20, view_width / view_height, 0.1, 10000
            );

            setup_lights(this.scene);
            setup_grid(this.scene);
            setup_input(this, element);
        }
    };

    this.View.prototype.clear_traces = function () {
        if (this.traces) {
            this.scene.remove(this.traces);
            this.traces = new THREE.Object3D();
            this.scene.add(this.traces);
        }
        this.render();
    };

    var color_from_string = function (s) {
        return parseInt(s.slice(1), 16);
    };

    var color_from_string_times = function (s, factor) {
        factor = factor || 1;
        var r = parseInt(s.slice(1, 3), 16),
            g = parseInt(s.slice(3, 5), 16),
            b = parseInt(s.slice(5, 7), 16);
        return ~~(r * factor) << 16 ^ ~~(g * factor) << 8 ^ ~~(b * factor);
    };

    this.View.prototype.draw_traces = function (data, colors) {
        console.log("draw_trace");

	var system, tmpdata, start, end, geometry, trace, line, i, j;

        for (system in data) {
            tmpdata = data[system];

	    // Draw succeeded rays
            geometry = new THREE.Geometry();
	    for (i=0; i < tmpdata.succeeded.length; i++) {
		trace = tmpdata.succeeded[i];
                for (j=0; j<trace.length-1; j++ ) {
                    if (trace[j][0] === NaN)
                        break;
                    start = new THREE.Vector3(
                        trace[j][0], trace[j][1], trace[j][2]),
                    geometry.vertices.push(start);
		    end = new THREE.Vector3(
                        trace[j+1][0], trace[j+1][1], trace[j+1][2]);
                    geometry.vertices.push(end);
                }
            }
            line = new THREE.Line(
                geometry, new THREE.LineBasicMaterial( {
                    //color: color_from_string_times(colors[system], Math.random()),
                    color: color_from_string_times(colors[system]),
                    opacity: 0.5, linewidth: 1} ), THREE.LinePieces);
            this.traces.add(line);

	    // Draw failed rays
            geometry = new THREE.Geometry();
	    for (i=0; i < tmpdata.failed.length; i++) {
		trace = tmpdata.failed[i];
                for (j=0; j<trace.length - 1; j++ ) {
                    if (trace[j][0] === NaN)
                        break;
                    start = new THREE.Vector3(
                        trace[j][0], trace[j][1], trace[j][2]);
                    geometry.vertices.push(start);
                    end = new THREE.Vector3(
                        trace[j+1][0], trace[j+1][1], trace[j+1][2]);
                    geometry.vertices.push(end);
                }
	    }
            line = new THREE.Line(
                geometry, new THREE.LineDashedMaterial( {
                    color: color_from_string_times(colors[system]),
                    dashSize: 1,
                    gapSize: 0.5} ), THREE.LinePieces);
            this.traces.add(line);
        }
        this.render();
    };

    this.View.prototype.render = function (mouse_coords) {
	this.theta = this.start_theta - 2 * (this.mouse_pos.x - this.mouse_start.x);
	this.phi = Math.min(Math.PI/2,
                            Math.max(-Math.PI/2, this.start_phi + 2 *
                                     (this.mouse_pos.y - this.mouse_start.y)));

        this.camera.position.x = 40 * Math.sin(this.theta) * Math.cos(this.phi);
        this.camera.position.y = 40 * Math.sin(this.phi);
	this.camera.position.z = 40 * Math.cos(this.theta) * Math.cos(this.phi);
        this.camera.width = 20 * this.scale;
        this.camera.height = 20 * this.scale;
        this.camera.updateProjectionMatrix();
	this.camera.lookAt( this.scene.position );

        this.renderer.clear();
        this.renderer.render( this.scene, this.camera );
        this.renderer.clear( false, true, false ); // clear depth buffer
        this.renderer.render( this.overlay, this.camera );    // render overlay
    };

    // Create a THREE mesh out of vertex/face lists
    function make_mesh (verts, faces) {
        var geom = new THREE.Geometry();
        verts.forEach(function (vert) {
            geom.vertices.push(new THREE.Vector3(vert[0], vert[1], vert[2]));
        });
        faces.forEach(function (face) {
            geom.faces.push(new THREE.Face3(face[0], face[1], face[2]));
        });
        geom.computeFaceNormals();
        geom.computeVertexNormals();
        var mesh = new THREE.Object3D();
        //mesh.eulerOrder = "ZYX";
        var frontmat = new THREE.MeshLambertMaterial({ color: 0xFFFF00,
                                                       side: THREE.FrontSide,
                                                       shading: THREE.SmoothShading,
                                                     });
        mesh.front = new THREE.Mesh( geom, frontmat );
        mesh.add(mesh.front);
        var backmat = new THREE.MeshLambertMaterial({ color: 0xFF00FF,
                                                      side: THREE.BackSide,
                                                      shading: THREE.SmoothShading
                                                    });
        mesh.back = new THREE.Mesh( geom, backmat  );
        mesh.add(mesh.back);
        return mesh;
    };

    // Take a list of mesh vertices and make a line running along the edges of it.
    function make_outline (verts) {
        var geom = new THREE.Geometry(), x, y, res = 11;
        for(x = 0; x < res-1; x++)
            geom.vertices.push(new THREE.Vector3(verts[x][0], verts[x][1], verts[x][2]));
        for(x = res-1; x <= res*res; x+=res)
            geom.vertices.push(new THREE.Vector3(verts[x][0], verts[x][1], verts[x][2]));
        for(x = res*res-1; x > res*(res-1); x--)
            geom.vertices.push(new THREE.Vector3(verts[x][0], verts[x][1], verts[x][2]));
        for(x = res*(res-1); x >= 0; x-=res)
            geom.vertices.push(new THREE.Vector3(verts[x][0], verts[x][1], verts[x][2]));
        var outline = new THREE.Line(
            geom, new THREE.LineBasicMaterial({color: 0xFFFFFF, linewidth: 2}),
            THREE.LineStrip);
        return outline;
    };


    // Construct a THREE object that represents an optical element
    // with an XYZ-axis.
    function make_axis () {
        var axis = new THREE.Object3D();
        var origin = new THREE.Vector3(0, 0, 0);
        var x1 = new THREE.Vector3(1, 0, 0);
        var y1 = new THREE.Vector3(0, 1, 0);
        var z1 = new THREE.Vector3(0, 0, 1);

        var geometry = new THREE.Geometry();
        geometry.vertices.push(origin);
        geometry.vertices.push(x1);
        axis.add(new THREE.Line(geometry, new THREE.LineBasicMaterial(
            {linewidth: 2, color: 0xFF0000})));

        geometry = new THREE.Geometry();
        geometry.vertices.push(origin);
        geometry.vertices.push(y1);
        axis.add(new THREE.Line(geometry, new THREE.LineBasicMaterial(
            {linewidth: 2, color: 0x00FF00})));

        geometry = new THREE.Geometry();
        geometry.vertices.push(origin);
        geometry.vertices.push(z1);
        axis.add(new THREE.Line(geometry, new THREE.LineBasicMaterial(
            {linewidth: 2, color: 0x0000FF})));

        return axis;
    };

    // An overlay object visualizing a selected representation
    var Selection = function (view, repr) {
        this.overlay = view.overlay;
        this.repr = repr;

        this.obj = new THREE.Object3D();  // the main container
        this.obj.position = repr.obj.position;
        this.obj.rotation = repr.obj.rotation;
        this.overlay.add(this.obj);

        this.outline = new THREE.Object3D();  // mesh outline
        this.outline.visible = false;
        this.obj.add(this.outline);

        this.axis = make_axis();
        // this.axis.position = this.obj.position;
        // this.axis.rotation = this.obj.rotation;
        this.axis.visible = false;
        this.obj.add(this.axis);
    };

    Selection.prototype.set_visible = function (visible) {
        this.outline.visible = visible;
        this.axis.traverse(function(obj) {obj.visible = visible;});
    };

    Selection.prototype.update = function (meshdata) {
        this.obj.remove(this.outline);
        var visible = this.axis.visible;
        var outline = make_outline(meshdata.verts);
        outline.visible = this.outline.visible;
        outline.position = this.repr.mesh.position;
        outline.rotation = this.repr.mesh.rotation;
        outline.visible = visible;
        this.outline = outline;
        this.obj.add(this.outline);
    };


    // A representation of an item
    this.Representation = function (view, meshdata, args) {
	var self = this;

        this.view = view;
        //this.frames = [];
	this.obj = new THREE.Object3D();
        //this.obj.add(make_axis());
        view.scene.add(this.obj);
        this.selection = new Selection(view, this);
        if (meshdata) {
            this.set_mesh(meshdata);
        } else {
            this.mesh = new THREE.Mesh();
        }
        this.update(args);

        view.render();
    };

    this.Representation.prototype.remove = function () {
        this.view.scene.remove(this.obj);
        this.view.overlay.remove(this.axis);
        this.view.overlay.remove(this.outline);
        this.view.render();
    };

    this.Representation.prototype.update = function (args) {
        console.log("update repr", args);
        // var position = args.frames[0].args.position, rotation = args.frames[0].args.rotation,
	var position = {x: 0, y: 0, z: 0}, rotation = {x: 0, y: 0, z: 0},
            radians = Math.PI / 180;
	for (var i=args.frames.length-1; i>=0; i--) {
	    position.x += args.frames[i].args.position.x;
	    position.y += args.frames[i].args.position.y;
	    position.z += args.frames[i].args.position.z;

	    rotation.x += args.frames[i].args.rotation.x;
	    rotation.y += args.frames[i].args.rotation.y;
	    rotation.z += args.frames[i].args.rotation.z;
	}
        this.obj.position.set(position.x, position.y , position.z);
        this.obj.rotation.set(rotation.x * radians,
                              rotation.y * radians,
                              rotation.z * radians);
        // this.mesh.position.set(offset.x, offset.y, offset.z);
        // this.mesh.rotation.set(alignment.x* radians,
        //                        alignment.y * radians,
        //                        alignment.z * radians);
        this.view.render();
    };

    this.Representation.prototype.highlight = function(high) {
        this.selection.set_visible(high);
        this.view.render();
    };

    this.Representation.prototype.set_mesh = function (meshdata) {
        var mesh = make_mesh(meshdata.verts, meshdata.faces),
            pos = this.mesh.position, rot = this.mesh.rotation;
        this.obj.remove(this.mesh);
        this.mesh = mesh;
        this.obj.add(this.mesh);
        mesh.position = pos;
        mesh.rotation = rot; //.set(rot.x, rot.y, rot.z);
        this.selection.update(meshdata);
        this.view.render();
    };

    return this;
})();
