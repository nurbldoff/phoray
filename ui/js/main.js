(function () {

    var schemas = {},
        curr_id = 0,
        view = new view3d.View(document.getElementById("view"));

    // function uniqueid(){
    //     // always start with a letter (for DOM friendlyness)
    //     var idstr=String.fromCharCode(Math.floor((Math.random()*25)+65));
    //     do {
    //         // between numbers and characters (48 is 0 and 90 is Z (42-48 = 90)
    //         var ascicode=Math.floor((Math.random()*42)+48);
    //         if (ascicode<58 || ascicode>64){
    //             // exclude all chars between : (58) and @ (64)
    //             idstr+=String.fromCharCode(ascicode);
    //         }
    //     } while (idstr.length<32);

    //     return (idstr);
    // }

    // Helper to create a JS model from schema, with optional defaults
    var create = function(schemas, kind, type, old) {
        var obj = {type: type, args: {}},
            schema = schemas[kind][type];
        for (var property in schema) {
            var subtype = schema[property].type;
            if (subtype == "geometry") {
                var oldgeo = (old && old.args.geometry.value) || null;
                obj.args[property] = {type: "geometry",
                                      value: create(schemas, "geometry", "Plane", oldgeo)};
            } else {
                var value = (old && property in old.args && old.args[property].value) ||
                        schema[property].value;
                obj.args[property] = {type: subtype, value: value};
            }
        }
        obj.id = (old && old.id) || curr_id++;
        return obj;
    };


    // Abstract representation of an item, for inheriting
    function Item() {

        var self = this;

        // If the type of the element is changed, we need to regenerate from schema
        self.type.subscribe(function (type) {
            var data = create(schemas, self.kind, type, ko.mapping.toJS(self));
            for (var prop in self.args) {
                if (!(prop in data.args)) {
                    delete self.args[prop];
                }
            }
            ko.mapping.fromJS(data, self);
        });
    };

    Item.prototype.get_types = function () {
        return Object.keys(schemas[this.kind]);
    };

    Item.prototype.get_properties = function () {
        var properties = Object.keys(schemas[this.kind][this.type()]);
        return properties;
    };


    // A geometry item
    function Geometry(data) {

        var self = this;
        self.kind = "geometry";
        self.mesh = ko.observable();

        ko.mapping.fromJS(data, {}, self);

        Item.call(self);

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
        self.kind = "element";

        self.mapping = {
            geometry: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data.id);
                },
                create: function (options) {
                    var geometry = new Geometry(options.data.value);
                    return {type: ko.observable("geometry"), value: geometry};
                }
            }
        };
        ko.mapping.fromJS(data, self.mapping, self);
        Item.call(self);

        // 3d representation
        self.repr = new view3d.Representation(view, null, ko.mapping.toJS(self.args));

        // Update the representation if the geometry's mesh changes
        self.args.geometry.value.mesh.subscribe(function (mesh) {
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
        self.kind = "source";

        ko.mapping.fromJS(data, {}, self);

        Item.call(self);
    };

    Source.prototype = Object.create(Item.prototype);


    // An optical system item, i.e. a collection of sources and elements
    function OpticalSystem (data) {

        var self = this;
        self.kind = "system";


        self.mapping = {
            elements: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data.id);
                },
                create: function (options) {
                    return new Element(options.data);
                }
            },
            sources: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data.id);
                },
                create: function (options) {
                    return new Source(options.data);
                }
            }
        };
        ko.mapping.fromJS(data, self.mapping, self);

        Item.call(self);
    };

    OpticalSystem.prototype = Object.create(Item.prototype);


    // Main model, a collection of optical systems
    var MainViewModel = function () {
        var self = this;

        //self.systems = ko.observableArray([]);
        self.selected_system = ko.observable(null);
        self.selected_element = ko.observable(null);

        self.mapping = {
            systems: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data.id);
                },
                create: function (options) {
                    return new OpticalSystem(options.data);
                },
            }
        };
        ko.mapping.fromJS({systems: []}, self.mapping, self);

        // Ask the server what kinds of objects it supports
        $.get("/schema",
              function (data) {
                  schemas = data;
              });

        // If the server already has a system defined, let's use it
        $.get("/system",
              function (data) {
                  // We need to update the current ID so we don't overlap
                  data.systems.forEach(function (sys) {
                      sys.elements.concat(sys.sources).forEach(function (ele) {
                          curr_id = Math.max(curr_id, ele.id) + 1;
                      });
                      curr_id = Math.max(curr_id, sys.id);
                  });
                  ko.mapping.fromJS(data, self.mapping, self);

                  // Start listening for any changes in the model, and
                  // if they happen, send everything to the server.
                  self.listener = ko.computed(function () {
                      self.send();
                  });  // .extend({throttle: 0});
              });

        self.send = function () {
            var data = ko.mapping.toJS(self);
            $.ajax({url: "/system", type: "POST",
                    data: JSON.stringify(data), contentType: "application/json",
                    success: function (data) {
                        //self.set(data);
                        if (data.systems.length > 0) {
                            // This means the system generated on the server was different
                            // from the client's one, so we have to update it. Could this
                            // lead to a loop?
                            ko.mapping.fromJS(data.systems, self.mapping, self.systems);
                        }
                        var system = self.selected_system();
                        if (system) {
                            self.trace();
                        }
                    }});
        };

        self.trace = function () {
            $.get("/trace", {n: 100, system: self.systems.indexOf(self.selected_system())},
                  function (data) {
                      view.clear_traces();
                      view.draw_traces(data.traces, self.selected_system().sources().map(
                          function(src) {return src.args.color.value()}));
                  });
        };

        $( "#footprint" ).dialog({ autoOpen: false, width: 300, height: 300 });
        self.footprint = function (element) {
            var sys_index = self.systems.indexOf(self.selected_system()),
                ele_index = self.selected_system().elements.indexOf(self.selected_element);
            $.get("/footprint", {element: ele_index, system: sys_index},
                  function (data) {
                      $("#footprint").empty();
                      $("#footprint").dialog("option",
                                             {title: "Footprint: " + self.selected_element().type()});
                      $("#footprint").dialog("open");
                      //plot( data.footprint, "#footprint");
                      var datasets = [];
                      for (var source in data.footprint) {
                          var color = self.systems()[sys_index].sources()[source]
                                  .args.color.value();
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

        self.add_system = function () {
            var systemdata = create(schemas, "system", "Free");
            systemdata.elements = [];
            systemdata.sources = [];
            var system = new OpticalSystem(systemdata);
            self.systems.push(system);
            self.selected_system(system);
        };

        self.add_element = function () {
            var element = new Element(create(schemas, "element", "Mirror"));
            self.selected_system().elements.push(element);
            self.selected_element(element);
        };

        self.add_source = function () {
            var source = new Source(create(schemas, "source", "GaussianSource"));
            self.selected_system().sources.push(source);
            self.selected_element(source);
        };

        self.select_system = function (system) {
            self.selected_element(null);
            self.selected_system(system);
        };

        self.select_element = function (element, system) {
            self.selected_system(system);
            self.selected_element(element);
        };

        self.remove_element = function () {
            var element = self.selected_element(),
                list = self.selected_system()[element.kind + "s"],
                index = list.indexOf(element);
            element.repr.remove();
            list.remove(element);
            self.selected_element(list()[index]);
        };

        self.move_element_up = function () {
            var element = self.selected_element(),
                list = self.selected_system()[element.kind + "s"];
            var index = list.indexOf(element);
            if (index > 0) {
                list.remove(element);
                list.splice(index - 1, 0, element);
            }
        };

        self.move_element_down = function () {
            var element = self.selected_element(),
                list = self.selected_system()[element.kind + "s"];
            var index = list.indexOf(element);
            if (index < list().length-1) {
                list.remove(element);
                list.splice(index + 1, 0, element);
            }
        };

    };

    ko.applyBindings(new MainViewModel());
})();