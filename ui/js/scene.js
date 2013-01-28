/* TODO: This is just a bunch of THREE stuff thrown together.
 * It should be structured. */

var view3d = (function () {

    var self = {};

    if (!Detector.webgl) {
        var warning = Detector.getWebGLErrorMessage();
        document.getElementById('view').appendChild(warning);
    } else {
        var renderer = new THREE.WebGLRenderer({antialias: true});
        //var renderer = new THREE.CanvasRenderer({antialias: false});
        var element = document.getElementById("view"),
            view_width = element.offsetWidth, view_height = element.offsetHeight;

        element.parentNode.replaceChild(renderer.domElement, element);
        element = renderer.domElement;
        element.id = "view";
        renderer.setSize( view_width, view_height );

        var scene = new THREE.Scene();
        self.scene = scene;

        // var camera = new THREE.PerspectiveCamera(
        //     25,             // Field of view
        //     view_width / view_height,      // Aspect ratio
        //     0.1,            // Near plane
        //     10000           // Far plane
        // );
        var camera = new THREE.OrthographicAspectCamera(
            20, view_width / view_height, 0.1, 10000
        );

        scene.add( camera );

        var light = new THREE.DirectionalLight( 0xFFFFFF, 0.5 );
        light.position.set( 10, 0, 5 );
        light.lookAt( scene.position );
        scene.add( light );

        var light = new THREE.DirectionalLight( 0xFFFFFF, 1.0 );
        light.position.set( -10, 10, 5 );
        light.lookAt( scene.position );
        scene.add( light );

        var light = new THREE.DirectionalLight( 0xFFFFFF, 0.5 );
        light.position.set( 0, -10, -5 );
        light.lookAt( scene.position );
        scene.add( light );

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

        var theta = -Math.PI / 4, start_theta = theta,
            phi = Math.PI / 6, start_phi = phi,
            mouse_start = {x: 0, y: 0}, mouse_pos= {x: 0, y: 0}, mouse_down = false,
            scale = 1;

        element.onmousedown = function ( event) {
            event.preventDefault();

	    mouse_start = {x: ( event.clientX / element.offsetWidth ) * 2 - 1,
	                   y: ( event.clientY / element.offsetHeight ) * 2 + 1};
            start_theta = theta;
            start_phi = phi;

            mouse_down = true;
        };

        element.onmouseup = function ( event ) {
            mouse_down = false;
        };

        element.onmousemove = function ( event ) {

	    event.preventDefault();

            if (mouse_down) {
	        mouse_pos = {x: ( event.clientX / element.offsetWidth ) * 2 - 1,
	                     y: ( event.clientY / element.offsetHeight ) * 2 + 1};
                self.render();
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
                scale *= 1.1;
            } else {
                scale /= 1.1;
            }
            self.render();
        });

        self.render = function (mouse_coords) {
	    theta = start_theta - 2 * (mouse_pos.x - mouse_start.x);
	    phi = Math.min(Math.PI/2,
                           Math.max(-Math.PI/2, start_phi + 2 * (mouse_pos.y - mouse_start.y)));

            camera.position.x = 40 * Math.sin(theta) * Math.cos(phi);
            camera.position.y = 40 * Math.sin(phi);
	    camera.position.z = 40 * Math.cos(theta) * Math.cos(phi);
            camera.width = 20 * scale;
            camera.height = 20 * scale;
            camera.updateProjectionMatrix();
	    camera.lookAt( self.scene.position );

            renderer.render( scene, camera );
        };

        //window.scene = scene;
        //self.render();
    }

    var rotateAroundWorldAxis = function ( object, axis, radians ) {
        var rotWorldMatrix = new THREE.Matrix4();
        rotWorldMatrix.makeRotationAxis(axis, radians);
        rotWorldMatrix.multiplySelf(object.matrix); // pre-multiply
        object.matrix = rotWorldMatrix;
        object.rotation.setEulerFromRotationMatrix(object.matrix, object.order);
    };

    self.set_global_rotation = function ( object, rotation ) {
        object.rotation.set(rotation.x, rotation.y, rotation.z);
        // object.rotation.x = rotation.x;
        // object.rotation.y = rotation.y;
        // object.rotation.z = rotation.z;

        // object.rotation.set(0, 0, 0);
        // object.matrix = new THREE.Matrix4();
        // rotateAroundWorldAxis(object, new THREE.Vector3(1, 0, 0), rotation.x);
        // rotateAroundWorldAxis(object, new THREE.Vector3(0, 1, 0), rotation.y);
        // rotateAroundWorldAxis(object, new THREE.Vector3(0, 0, 1), rotation.z);
    };

    // Create a THREE mesh out of vertex/face lists
    self.make_mesh = function (verts, faces) {
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
                                                       shading: THREE.SmoothShading
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
    // with a mesh and an XYZ-axis.
    self.make_repr = function (mesh) {
        var obj, axis, geometry;
        axis = new THREE.Object3D();
        var origin = new THREE.Vector3(0, 0, 0);
        var x1 = new THREE.Vector3(1, 0, 0);
        var y1 = new THREE.Vector3(0, 1, 0);
        var z1 = new THREE.Vector3(0, 0, 1);

        geometry = new THREE.Geometry();
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

        obj = new THREE.Object3D();
        obj.add(axis);
        obj.add(mesh);

        return {repr: obj, axis: axis};
    };

    var optaxis = null;
    // Draw an "optical axis"
    console.log("jej");
    self.draw_optaxis = function (data) {
        self.scene.remove(optaxis);
        var axis = data.axis;
        optaxis = new THREE.Object3D();
        var geometry = new THREE.Geometry();
        axis.forEach(function (point) {
            var position = new THREE.Vector3(point.x, point.y, point.z);
            geometry.vertices.push(position);
            geometry.computeLineDistances();
            var line = new THREE.Line(
                geometry, new THREE.LineDashedMaterial( {
                    color: 0xffff00, linewidth: 1.0, dashSize: 0.2, gapSize: 0.1 } ),
                THREE.LinePiece);
            optaxis.add(line);
            });
        self.scene.add(optaxis);
        self.render();
    };

    self.traces = null;
    // draw lines representing rays going through the system
    self.render_traces = function (data) {
        self.scene.remove(scene.traces);
        self.scene.traces = new THREE.Object3D();
        data.forEach( function (trace) {
            var geometry = new THREE.Geometry();
            for ( var i=0; i<trace.length; i++ ) {
                var position = new THREE.Vector3(
                    trace[i][0], trace[i][1], trace[i][2]);
                geometry.vertices.push(position);
            }
            var line = new THREE.Line(
                geometry, new THREE.LineBasicMaterial( {
                    color: 0xffffff, opacity: 0.5, linewidth: 0.5} ));
            self.scene.traces.add(line);
        });
        self.scene.add(scene.traces);
        self.render();
    };

    self.remove_traces = function () {
        self.scene.remove(self.scene.traces);
        self.render();
    };

    return self;

}());
