(function () {

    // This represents the list of arguments for an object
    function Arguments(schema, spec) {
        var self = this;

        self._schema = schema;
        spec = spec || {};

        // create observable properties for each argument
        for(var prop in schema) {
            var type = schema[prop].type,
                value = schema[prop].value,
                old_prop = spec[prop];

            switch (type) {
            case "string":
                self[prop] = new ko.observable(old_prop || value || "");
                break;
            case "number":
                self[prop] = new ko.numericObservable(old_prop || value || 0);
                break;
            case "length":
                self[prop] = new ko.numericObservable(old_prop || value || 0);
                break;
            case "angle":
                self[prop] = new ko.numericObservable(old_prop || value || 0);
                break;
            case "position":
                self[prop] = old_prop ?
                    new ko.observableVector(old_prop.x, old_prop.y, old_prop.z) :
                    (prop.value !== undefined ?
                     new ko.observableVector(value.x, value.y, value.z) :
                     new ko.observableVector(0, 0, 0));
                break;
            case "rotation":
                self[prop] = old_prop ?
                    new ko.observableVector(old_prop.x, old_prop.y, old_prop.z) :
                    (prop.value !== undefined ?
                     new ko.observableVector(value.x, value.y, value.z) :
                     new ko.observableVector(0, 0, 0));
                break;
            case "geometry":
                self[prop] = new Geometry(geometry_defs, old_prop || {type: "Plane"});
                break;
            }
        }

        self.toJSON = function () {
            var js = ko.toJS(self);
            delete js._schema;
            return js;
        };

        self.schema = function () {
            schema = [];
            for (var key in self._schema) {
                schema.push({name: key, type: self._schema[key].type});
            };
            return schema;
        };

        // Update the arguments
        self.set = function (new_spec) {
            for (var key in new_spec) {
                var value = new_spec[key],
                    type = self._schema[key].type;
                switch(type) {
                case "geometry":
                    self[key].args().set(value.args);
                    break;
                case "position":
                    var pos = self[key];
                    for (var axis in value) {
                        pos[axis](value[axis]);
                    }
                    break;
                case "rotation":
                    var rot = self[key];
                    for (var axis in value) {
                        rot[axis](value[axis]);
                    }
                    break;
                default:
                    self[key](value);
                }
            }
        };

    }

    // An abstract "item" that has a type and some arguments
    function Item(schemas, spec) {
        var self = this;

        self.type = new ko.observable(spec.type);
        self.type.choices = Object.keys(schemas);

        self.args = new ko.observable(new Arguments(schemas[spec.type], spec.args));

        self.type.subscribe(function (new_type) {
            self.args(new Arguments(schemas[new_type], ko.toJS(self.args)));
        });

        self.set = function (new_spec) {
            if (new_spec) {
                if (new_spec.type) {
                    self.type(new_spec.type);
                }
                if (new_spec.args) {
                    self.args().set(new_spec.args);
                }
            }
        };
    }

    // Representation of a surface
    function Geometry(schemas, spec) {
        var self = this;

        Item.call(self, schemas, spec);

        self.changed = ko.computed(function () {
            return ko.toJS(self);
        });

        self.toJSON = function () {
            var js = ko.toJS(self);
            delete js.changed;
            return js;
        };
    }


    // Generalized member of an optical system
    function Member(schemas, spec) {

        var self = this;
        Item.call(self, schemas, spec);
    }

    // A 3D representation
    function Representation(mesh) {

        var self = this;

        var position = new ko.computed( function () {
            return self.args().position();
        });

        var rotation = new ko.computed( function () {
            return self.args().rotation();
        });

        var offset = new ko.computed( function () {
            if (self.args().offset) {
                return self.args().offset();
            } else {
                return {x:0, y:0, z:0};
            }
            // var position = self.position(),
            //     offset = self.args().offset();
            // return {x: position.x + offset.x,
            //         y: position.y + offset.y,
            //         z: position.z + offset.z};
        });

        var alignment = new ko.computed( function () {
            if (self.args().alignment) {
                return self.args().alignment();
            } else {
                return {x:0, y:0, z:0};
            }
        });

        self.set_repr = function (new_mesh) {
            new_mesh.position = mesh.position;
            new_mesh.rotation = mesh.rotation;
            repr.remove(mesh);
            repr.add(new_mesh);

            mesh = new_mesh;
            view3d.render();
        };
        self.selected = function (on) {
            if (on) {
                if (mesh.front) {
                    var col = mesh.front.material.color,
                        emi = mesh.front.material.emissive;
                    emi.r = 0.1 + col.r * 0.5;
                    emi.g = 0.1 + col.g * 0.5;
                    emi.b = 0.1 + col.b * 0.5;

                    col = mesh.back.material.color,
                    emi = mesh.back.material.emissive;
                    emi.r = 0.1 + col.r * 0.5;
                    emi.g = 0.1 + col.g * 0.5;
                    emi.b = 0.1 + col.b * 0.5;
                } else {
                    col = mesh.material.color,
                    emi = mesh.material.emissive;
                    emi.r = 0.1 + col.r * 0.5;
                    emi.g = 0.1 + col.g * 0.5;
                    emi.b = 0.1 + col.b * 0.5;
                }
            } else {
                if (mesh.front) {
                    mesh.front.material.emissive = new THREE.Color( 0x000000);
                    mesh.back.material.emissive = new THREE.Color( 0x000000);
                } else {
                    mesh.material.emissive = new THREE.Color( 0x000000);
                    mesh.material.emissive = new THREE.Color( 0x000000);
                }
            }
            axis.traverse(function (child) {
                child.visible = on;
            });
            view3d.render();
        };

        var update_position = function (pos) {
            repr.position.set(pos.x, pos.y, pos.z);
        };
        position.subscribe(update_position);

        var update_rotation = function (rot) {
            view3d.set_global_rotation(repr, {
                x: rot.x / 180 * Math.PI,
                y: rot.y / 180 * Math.PI,
                z: rot.z / 180 * Math.PI
            });
        };
        rotation.subscribe(update_rotation);

        var update_offset = function (pos) {
            mesh.position.set(pos.x, pos.y, pos.z);
        };
        offset.subscribe(update_offset);

        var update_alignment = function (rot) {
            view3d.set_global_rotation(mesh, {
                x: rot.x / 180 * Math.PI,
                y: rot.y / 180 * Math.PI,
                z: rot.z / 180 * Math.PI
            });
        };
        alignment.subscribe(update_alignment);

        self.remove_repr = function () {
            repr.remove(mesh);
            view3d.scene.remove(repr);
            view3d.render();
        };

        // THREE.js representation
        var result = view3d.make_repr(mesh);
        var repr = result.repr, axis = result.axis;
        view3d.scene.add(repr);
        self.selected(false);
        update_position(self.args().position());
        update_rotation(self.args().rotation());
        update_offset(self.args().offset());
        update_alignment(self.args().alignment());
        //view3d.render();
    };

    // An optical element
    var Element = function (schema, spec) {
        var self = this;

        Member.call(self, schema, spec);
        $.get("/mesh", {geometry: ko.toJSON(self.args().geometry), resolution: 10},
              function(data) {
                  Representation.call(self, view3d.make_mesh(data.verts, data.faces));
              });

        self.get_mesh = function () {
            $.get("/mesh", {geometry: ko.toJSON(self.args().geometry), resolution: 10},
                  function(data) {
                      self.set_repr(view3d.make_mesh(data.verts, data.faces));
                  });
        };

        self.args().geometry.changed.subscribe(self.get_mesh);
    };


    // A lightsource
    var Source = function (schema, spec) {
        var self = this;

        Member.call(self, schema, spec);

        // TODO: this is a placeholder, not sure how to best represent a source
        Representation.call(self, new THREE.Mesh(
            new THREE.CubeGeometry( 0.2, 0.2, 0.2 ),
            new THREE.MeshLambertMaterial( { color: 0x00FFFF } )
        ));
    };


    function OpticalSystem() {
        var self = this;

        Member.call(self, system_defs, {type: "Free"});

        self.elements = ko.observableArray([]);
        self.sources = ko.observableArray([]);

        var traces = null;

        self.add_element = function () {
            var element = new Element(element_defs, {type: "Mirror"});
            self.elements.push(element);
        };

        self.add_source = function () {
            var source = new Source(source_defs, {type: "GaussianSource"});
            self.sources.push(source);
        };

        var _elements_or_sources = function (something) {
            if (self.elements.indexOf(something) >= 0) {
                return self.elements;
            } else {
                return self.sources;
            }
        };

        self.remove = function (element) {
            element.remove_repr();
            _elements_or_sources(element).remove(element);
            delete(element);
        };

        self.move_up = function (element) {
            var where = _elements_or_sources(element),
                index = where.indexOf(element);
            if (index > 0) {
                where.splice(index, 1);
                where.splice(index - 1, 0, element);
            }
        };

        self.move_down = function (element) {
            var where = _elements_or_sources(element),
                index = where.indexOf(element);
            if (index < where().length - 1) {
                where.splice(index, 1);
                where.splice(index + 1, 0, element);
            }
        };

        self.set = function (new_spec) {
            if (new_spec.elements) {
                for (var i=0; i<new_spec.elements.length; i++) {
                    var spec = new_spec.elements[i];
                    if (!self.elements()[i]) {
                        var element = new Element(element_defs, spec);
                        self.elements.push(element);
                    } else {
                        self.elements()[i].set(spec);
                    }
                }
            }
            if (new_spec.sources) {
                for (var i=0; i<new_spec.sources.length; i++) {
                    if (!self.sources()[i]) {
                        self.add_source();
                    }
                    self.sources()[i].set(new_spec.sources[i]);
                }
            }
        };

        self.trace = function () {
            $.get("/trace", {n: 100},
                  function (data) {
                      view3d.render_traces(data.traces);
                  });
        };

        self.footprint = function (element) {
            $.get("/footprint", {n: self.elements.indexOf(element)},
                  function (data) {
                      console.log("footprint", data);
                  });
        };

        self.clear_traces = function () {
            view3d.remove_traces();
        };
    }

    var system_defs, element_defs, source_defs, geometry_defs;

    function OpticalSystemsViewModel() {
        var self = this;

        self.systems = ko.observableArray([]);
        self.selected = ko.observable(null);

        self.selected_element = ko.observable(null);

        self.add_system = function () {
            var system = new OpticalSystem();
            self.systems.push(system);
            self.selected(system);
        };

        self.select_element = function (element) {
            if (self.selected_element()) {
                self.selected_element().selected(false);
            }
            element.selected(true);
            self.selected_element(element);
        };

        self.set = function (data) {
            for (var i=0; i<data.systems.length; i++) {
                if (!self.systems()[i]) {
                    self.add_system();
                }
                if (!!data.systems[i]) {
                    self.systems()[i].set(data.systems[i]);
                }
            }
        };

        var everything = ko.computed( function () {
            return ko.toJS(self.systems);
        }).extend({throttle: 100});

        everything.subscribe(function () {
            self.send();
            $.get("/axis", function(data) {
                view3d.draw_optaxis(data);
            });
        });

        self.send = function () {
            var jsdata = ko.toJSON({systems: self.systems});
            $.ajax({url: "/system", type: "POST",
                    data: jsdata, contentType: "application/json",
                    success: function (data) {
                        self.set(data);
                        view3d.render();
                    }});
        };

        // Ask the server what kinds of objects it supports
        $.get("/schema",
              function (data) {
                  system_defs = data.system;
                  element_defs = data.element;
                  source_defs = data.source;
                  geometry_defs = data.geometry;
              });

        // If the server already has a system defined, let's use it
        $.get("/system",
              function (data) {
                  self.set(data);
              });

    }

    ko.applyBindings(new OpticalSystemsViewModel());
    view3d.render();

})();