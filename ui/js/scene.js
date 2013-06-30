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
        var self = this;
        self.traces = null;
        this.traces = new THREE.Object3D();

        if (!Detector.webgl) {
            var warning = Detector.getWebGLErrorMessage();
            document.getElementById('view').appendChild(warning);

            // It should be possible to run with the canvas renderer if the webgl
            // backend doesn't work. Needs testing and probably some tweaking, though.
            //this.renderer = new THREE.CanvasRenderer({antialias: false});

        } else {
            this.renderer = new THREE.WebGLRenderer({antialias: true});

            var view_width = element.offsetWidth, view_height = element.offsetHeight;

            // Camera coodinates
            self.theta = -Math.PI / 4;
            self.start_theta = self.theta,
            self.phi = Math.PI / 6;
            self.start_phi = self.phi;
            self.mouse_start = {x: 0, y: 0};
            self.mouse_pos= {x: 0, y: 0};
            self.mouse_down = false;
            self.scale = 1;

            element.parentNode.replaceChild(this.renderer.domElement, element);
            element = this.renderer.domElement;
            element.id = "view";
            this.renderer.setSize( view_width, view_height );

            self.scene = new THREE.Scene();
            self.camera = new THREE.OrthographicAspectCamera(
                20, view_width / view_height, 0.1, 10000
            );

            setup_lights(self.scene);
            setup_grid(self.scene);
            setup_input(self, element);
        }
    };

    this.View.prototype.clear_traces = function () {
        if (this.traces) {
            this.scene.remove(this.traces);
            this.traces = new THREE.Object3D();
        }
        this.render();
    };

    var color_from_string = function (s) {
        return parseInt(s.slice(1), 16);
    };

    this.View.prototype.draw_traces = function (data, colors) {
        console.log("draw_trace", data, colors);
        for (var system in data) {
            var tmpdata = data[system];
            tmpdata.forEach( function (trace) {
                var geometry = new THREE.Geometry();
                for ( var i=0; i<trace.length; i++ ) {
                    if (trace[i][0] === NaN)
                        break;
                    var position = new THREE.Vector3(
                        trace[i][0], trace[i][1], trace[i][2]);
                    geometry.vertices.push(position);
                }
                var line = new THREE.Line(
                    geometry, new THREE.LineBasicMaterial( {
                        color: color_from_string(colors[system]),
                        opacity: 0.5, linewidth: 0.5} ));
                this.traces.add(line);
            }.bind(this));
        }
        this.scene.add(this.traces);
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

        this.renderer.render( this.scene, this.camera );
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


    // A representation of an item
    this.Representation = function (view, meshdata, args) {
        this.view = view;
        this.obj = new THREE.Object3D();
        this.obj.add(make_axis());
        if (meshdata) {
            this.set_mesh(meshdata);
        } else {
            this.mesh = new THREE.Mesh();
        }
        view.scene.add(this.obj);
        this.update(args);

        view.render();
    };

    this.Representation.prototype.remove = function () {
        this.view.scene.remove(this.obj);
        this.view.render();
    };

    this.Representation.prototype.update = function (args) {
        var position = args.position,
            rotation = args.rotation,
            offset = args.offset,
            alignment = args.alignment,
            radians = Math.PI / 180;
        this.obj.position.set(position.x, position.y , position.z);
        this.obj.rotation.set(rotation.x * radians,
                              rotation.y * radians,
                              rotation.z * radians);
        this.mesh.position.set(offset.x, offset.y, offset.z);
        this.mesh.rotation.set(alignment.x* radians,
                               alignment.y * radians,
                               alignment.z * radians);
        this.view.render();
    };

    this.Representation.prototype.set_mesh = function (meshdata) {
        var mesh = make_mesh(meshdata.verts, meshdata.faces),
            pos = this.mesh.position, rot = this.mesh.rotation;
        this.obj.remove(this.mesh);
        this.mesh = mesh;
        this.obj.add(this.mesh);
        mesh.position.set(pos.x, pos.y, pos.z);
        mesh.rotation.set(rot.x, rot.y, rot.z);
        this.view.render();
    };

    return this;
})();