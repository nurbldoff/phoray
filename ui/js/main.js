(function () {

    var schemas = {},
        view = new view3d.View(document.getElementById("view"));


    // Helper to create a JS model from schema, with optional default values
    var create = function(schemas, kind, type, old) {
        console.log("create", kind, type);
        var obj = {type: type, args: {}},
            schema = schemas[kind][type];
        for (var property in schema) {
            var subtype = schema[property].type;
            if (subtype == "geometry") {
                var oldgeo = (old && old.args.geometry) || null,
                    geotype = (oldgeo && oldgeo.type) || "Plane";
                obj.args[property] = create(schemas, "Surface", geotype, oldgeo);
            } else {
                var value = (old && property in old.args && old.args[property]) ||
                        schema[property].value;
                obj.args[property] = value;
            }
        }
        //obj.id = (old && old.id) || curr_id++;
        return obj;
    };


    // Abstract representation of an item, for inheriting
    function Item(data) {

        var self = this;

        self.update = function (type) {
            $.get("/create?what=" + self.kind, {}, function (data) {
                ko.mapping.fromJS(data, self);
            });
        };

        self.mapping = {
            args: {
                create: function (options) {
                    console.log("create Arguments");
                    return new Arguments(options.data);
                }
            }
        };

        ko.mapping.fromJS(data, self.mapping, self);

        // If the type of the item is changed, we need to regenerate from schema
        self.type.subscribe(function (type) {
            var data = create(schemas, self.kind, type, ko.mapping.toJS(self));
            self.args = new Arguments(data.args);
        });
    };

    Item.prototype.get_types = function () {
        return Object.keys(schemas[this.kind]);
    };

    Item.prototype.get_properties = function () {
        var schema = schemas[this.kind][this.type()];
        // var properties = ko.utils.arrayFilter(Object.keys(schema), function(item) {
        //     return schema[item].type != "list";
        // });
        // return properties;
        return Object.keys(schema);
    };

    Item.prototype.get_schema = function (prop) {
        //console.log("get schema", prop, schemas[this.kind][this.type()][prop]);
        return schemas[this.kind][this.type()][prop];
    };


    // A set of arguments.
    // The properties that defines an item.
    function Arguments(data) {

        var self = this;

        var mapping = {
            frames: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data._id);
                },
                create: function(options) {
                    console.log("create Frame");
                    return new Frame(options.data);
                }
            },
            elements: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data._id);
                },
                create: function (options) {
		    return new Element(options.data);
                }
            },
            sources: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data._id);
                },
                create: function (options) {
                    console.log("create source");
                    return new Source(options.data);
                }
            },
            geometry: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data._id);
                },
                create: function (options) {
                    console.log("geometry data", options.data);
                    return new Geometry(options.data);
                }
            }
        };

        ko.mapping.fromJS(data, mapping, self);
    }


    // A reference frame.
    // Used to position things in space.
    function Frame(data) {

        var self = this;
        self.kind = "Frame";

        Item.call(self, data);

    };
    Frame.prototype = Object.create(Item.prototype);


    // A geometry item.
    // Used to represent an item graphically.
    function Geometry(data) {

        var self = this;
        self.kind = "Surface";
        self.mesh = ko.observable();

        Item.call(self, data);

        // Update the mesh if properties change
        self.get_mesh = ko.computed( function () {
            var data = ko.mapping.toJSON(self);
            $.get("/mesh", {geometry: data, resolution: 10},
                  function(data) {
                      self.mesh(data);
                  });
        });
    };

    Geometry.prototype = Object.create(Item.prototype);


    // An optical element item
    function Element(data) {

        var self = this;
        self.kind = "Element";

        var mapping = {
            args: {
                create: function (options) {
                    console.log("arguments");
                    return new Arguments(options.data);
                }
            }
        };

        Item.call(self, data);

        // 3d representation
        self.repr = new view3d.Representation(view, null, ko.mapping.toJS(self.args));

        // Update the representation if the geometry's mesh changes
        self.args.geometry.mesh.subscribe(function (mesh) {
            self.repr.set_mesh(mesh);
        });

        // When a property changes, update the representation
        // TODO: this updates everything on any change. Could it be made more
        // efficient? Look at https://github.com/ZiadJ/knockoutjs-reactor
        ko.computed( function () {
            self.repr.update(ko.mapping.toJS(self.args));
        });

    };

    Element.prototype = Object.create(Item.prototype);


    // A lightsource item
    function Source(data) {

        var self = this;
        self.kind = "Source";

        Item.call(self, data);

    };

    Source.prototype = Object.create(Item.prototype);


    // An optical system item, i.e. a collection of sources and elements
    function OpticalSystem (data) {

        var self = this;
        self.kind = "System";

        // var mapping = {
        //     args: {
        //         create: function (options) {
        //             console.log("create Arguments");
        //             return new Arguments(options.data);
        //         }
        //     }
        // };

        Item.call(self, data);

        self.add_pelement = function () {
            console.log("add element");
            var data = {type: "Mirror"};
            $.get("/create?base=Element", data, function (data) {
                var element = new Element(data);
                self.args.elements.push(element);
            });
        };
    };

    OpticalSystem.prototype = Object.create(Item.prototype);


    // Main model, a collection of optical systems
    var MainViewModel = function () {
        var self = this;

	self.bases = {"System": OpticalSystem, "Source": Source, "Element": Element, "Frame": Frame};

        // these are 'internal' properties keeping track of selections
        self.selected_system = ko.observable(null);
        self.selected_element = ko.observable(null);
        self.selected_source = ko.observable(null);

        // self.selected_system = ko.computed(function () {
        //     self._selsys();
        //     if (self.systems)
        //         return self.systems()[self._selsys()];
        //     else
        //         return null;
        // });

        // self.selected_element = ko.computed(function () {
        //     self._selele();
        //     if (self.systems)
        //         return self.selected_system().args.elements()[self._selele()];
        //     else
        //         return null;
        // });

        // self.selected_source = ko.computed(function () {
        //     self._selsou();
        //     if (self.systems)
        //         return self.selected_system().args.sources()[self._selsou()];
        //     else
        //         return null;
        // });

        var mapping = {
            systems: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data._id);
                },
                create: function (options) {
                    return new OpticalSystem(options.data);
                }
            }
        };
        ko.mapping.fromJS({systems: []}, mapping, self);

        // Ask the server what kinds of objects it supports
        $.get("/schema",
              function (data) {
                  console.log("schemas", data);
                  schemas = data;
              });

        // If the server already has a system defined, let's use it
        $.get("/system",
              function (data) {
                  console.log("data", data);
                  ko.mapping.fromJS(data, mapping, self);
                  console.log("hej");
                  // Start listening for any changes in the model, and
                  // if they happen, send everything to the server.
                  self.listener = ko.pauseableComputed(function () {
                      self.send();
                  }); //.extend({throttle: 10});

              });

        // SockJS connection for Trace results
        // var sock = new SockJS('/traceconn');
        // sock.onopen = function() {
        //     console.log('open');
        //     sock.send({hej:1});
        // };
        // sock.onmessage = function(e) {
        //     console.log('message', e.data);
        //     self.draw_tbbbraces(e.data);
        // };
        // sock.onclose = function() {
        //     console.log('close');
        // };

        self.update = function (data) {
            // We need to avoid sending lots of times (and potential loops)
            // since the mapping update is not done atomically.
            // This is a crude way of doing it.
            self.listener.pause();
            ko.mapping.fromJS(data, self.mapping, self);
            self.listener.resume();
        };

        var _update = function (data) {
            //self.set(data);
            console.log("got", data);
            if (data.systems) {
                // This means the system generated on the server was different
                // from the client's one, so we have to update it.
                self.update(data);
            }
            var system = self.selected_system();
            if (system) {
                self.trace();
            }
        };

        var old_data_str = "";
        self.send = function () {
            var data = ko.mapping.toJS(self),
                data_str = JSON.stringify(data);
            if (data_str != old_data_str) {
                console.log("send", data);
                $.ajax({url: "/system", type: "POST",
                        data: data_str, contentType: "application/json",
                        success: _update});
                old_data_str = data_str;
            } else {
                console.log("Data unchanged; not sending.");
            }
        };

        var tracing = false,  // flag used to block new traces while tracing
            trace_queued = false;

        self.draw_traces = function (data) {
            view.clear_traces();
            view.draw_traces(data.traces, self.selected_system().args.sources().map(
                function(src) {return src.args.color();}));
            //tracing = false;
            // if (trace_queued) {
            //     trace_queued = false;
            //     self.trace();
            // }
        };

        // Ask the server to trace us some rays
        self.trace = function (n) {
            n = n || 1000;
            if (!tracing) {
                // No more tracing until we're done with this one. Primitive, but it will
                // have to do until the server is more asynchronous.
                tracing = true;
                //sock.send({n: n, system: self.systems.indexOf(self.selected_system())});
                $.get("/trace", {n: n, system: self.systems.indexOf(self.selected_system())},
                      function (data) {
                          console.log("Trace took", data.time, "s");
                          //console.log(data[0][0][1]);
                          tracing = false;
                          view.clear_traces();
                          view.draw_traces(data.traces,
                                           self.selected_system().args.sources().map(
                                               function(src) {return src.args.color();}));
                          // if (trace_queued) {
                          //     trace_queued = false;
                          //     self.trace();
                          // }
                      });
            }//  else {
            //     trace_queued = true;
            // }
        };

        $( "#footprint" ).dialog({ autoOpen: false, width: 300, height: 300 });
        self.footprint = function (element) {
            var sys_index = self.systems.indexOf(self.selected_system()),
                ele_index = self.selected_system().args.elements.indexOf(self.selected_element);
            $.get("/footprint", {element: ele_index, system: sys_index},
                  function (data) {
                      $("#footprint").empty();
                      $("#footprint").dialog("option",
                                             {title: "Footprint: " + self.selected_element().type()});
                      $("#footprint").dialog("open");
                      //plot( data.footprint, "#footprint");
                      var datasets = [];
                      for (var source in data.footprint) {
                          var color = self.systems()[sys_index].args.sources()[source]
                                  .args.color();
                          datasets.push({
                              label: source,
                              color: color,
                              data: data.footprint[source],
                              points: {
                                  fillColor: color
                              }
                          });
                      }
                      $.plot($("#footprint"), datasets, {
                          series: {
                              points: {
                                  radius: 2,
                                  show: true,
                                  fill: true,
                                  lineWidth: 0
                              }
                          },
                          grid: {
                              color: "#FFF",
                              backgroundColor: "rgba(0,0,0,0.5)"
                          },
                          shadowSize: 0
                      });
                  });
        };

        // Note: There is some confusion here. "element" sometimes refers to an Element and
        // sometimes either an Element or a Source.

        self.add_system = function () {
            var data = {type: "Free"};
	    console.log("create_system");
            $.get("/create?base=System", {}, function (data) {
                console.log("create_system", data);
                var system = new OpticalSystem(data);
                console.log("created system", system);
                self.systems.push(system);
                self.select_system(system);
            });
        };

        self.add_element = function (l) {
            var data = {type: "Mirror"};
            $.get("/create?base=Element", data, function (data) {
		console.log("add element", data);
                var element = new Element(data);
                l.value.push(element);
                self.select_element(element);
            });
        };

        self.add_source = function (l) {
            var data = {type: "GaussianSource"};
            $.get("/create?base=Source", data, function (data) {
                var source = new Source(data);
                l.value.push(source);
                self.select_source(source);
            });
        };

        self.add_frame = function (l) {
	    console.log("list", l);
            $.get("/create?base=Frame", {}, function (data) {
		console.log("frame", data);
                var frame = new Frame(data);
		l.value.push(frame);
            });
        };


        self.clone_element = function () {
            var original = ko.mapping.toJS(self.selected_element()),
                clone = new Element(create(schemas, "Element", original.type, original));
            self.selected_system().args.elements.push(clone);
            self.selected_element(clone);
        };

        self.clone_source = function () {
            var original = ko.mapping.toJS(self.selected_element()),
                clone = new Source(create(schemas, "Source", original.type, original));
            self.selected_system().sources.push(clone);
            self.selected_element(clone);
        };

        self.select_system = function (system) {
            self.selected_system(system);
            self.selected_element(null);
            self.selected_source(null);
        };

        self.select_element = function (element, system) {
            self.selected_source(null);
            //self.selected_system(null);
            if (!!system) {
                self.selected_system(system);
            }
            if (self.selected_element())
                self.selected_element().repr.highlight(false);
            self.selected_element(element);
            element.repr.highlight(true);
        };

        self.select_source = function (source, system) {
            self.selected_element(null);
            //self.selected_system(null);
            if (!!system) {
                self.selected_system(system);
            }
            self.selected_source(source);
        };

        self.remove_system = function () {
            var system = self.selected_system(),
                list = self.systems, index = list.indexOf(system);
            ko.utils.arrayForEach(system.args.elements(), function (element) {
                self.remove_element(element);});
            ko.utils.arrayForEach(system.args.sources(), function (source) {
                self.remove_source(source);});
            list.remove(system);
            index = Math.max(Math.min(list.length-1, index), 0);
            self.selected_system(list()[index]);
            view.clear_traces();
        };

        self.remove_element = function (element) {
            element = element || self.selected_element();
            var list = self.selected_system().args.elements,
                index = list.indexOf(element);
            element.repr.remove();
            list.remove(element);
            index = Math.max(Math.min(list.length-1, index), 0);
            self.selected_element(list()[index]);
        };

        self.remove_source = function (source) {
            source = source || self.selected_element();
            var list = self.selected_system().args.sources,
                index = list.indexOf(source);
            //source.repr.remove();
            list.remove(source);
            index = Math.max(Math.min(list.length-1, index), 0);
            self.selected_source(list()[index]);
        };

        self.move_element_up = function () {
            var element = self.selected_element(),
                list = self.selected_system().args.elements,
                index = list.indexOf(element);
            if (index > 0) {
                list.remove(element);
                list.splice(index - 1, 0, element);
            }
        };

        self.move_element_down = function () {
            var element = self.selected_element(),
                list = self.selected_system().args.elements,
                index = list.indexOf(element);
            if (index < list().length-1) {
                list.remove(element);
                list.splice(index + 1, 0, element);
            }
        };

    };

    // add up/down arrowkey behavior to numeric inputs
    $(document).on("keypress", "input[type=number]", updown);

    ko.applyBindings(new MainViewModel());
})();
