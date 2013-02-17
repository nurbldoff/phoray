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

    // Create a JS model from schema, with optional defaults
    var create = function(schemas, kind, type, old) {
        console.log("create", old);
        var obj = {type: type, args: {}},
            schema = schemas[kind][type];
        for (var property in schema) {
            console.log("property", property);
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
        //obj.id = (old && old.id) || uniqueid();
        console.log("created", obj);
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
        console.log("get_types", this.kind);
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
            console.log("get_mesh", data);
            $.get("/mesh", {geometry: data, resolution: 10},
                  function(data) {
                      console.log("mesh data", data);
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
            console.log("repr mesh changed", mesh);
            self.repr.set_mesh(mesh);
        });

        // When a property changes, update the representation
        // TODO: this updates everything on any change. Could it be made more
        // efficient? Look at https://github.com/ZiadJ/knockoutjs-reactor
        ko.computed( function () {
            console.log("change", self.id());
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
                    console.log("element", options.data);
                    return new Element(options.data);
                }
            },
            sources: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data.id);
                },
                create: function (options) {
                    console.log("source", options.data);
                    return new Source(options.data);
                }
            }
        };
        ko.mapping.fromJS(data, self.mapping, self);

        Item.call(self);
    };

    OpticalSystem.prototype = Object.create(Item.prototype);

    OpticalSystem.prototype.add_element = function () {
        var element = new Element(create(schemas, "element", "Mirror"));
        this.elements.push(element);
        this.selected_element(element);
    };

    OpticalSystem.prototype.add_source = function () {
        var source = new Source(create(schemas, "source", "GaussianSource"));
        this.sources.push(source);
        this.selected_element(source);
    };

    OpticalSystem.prototype.move_up = function (what) {
        // do something intelligent
    };

    OpticalSystem.prototype.trace = function () {
        $.get("/trace", {n: 100},
              function (data) {
                  console.log("got trace", data);
                  view.draw_traces(data.traces);
              });
    };


    // Main model, a collection of optical systems
    var MainViewModel = function () {
        var self = this;

        //self.systems = ko.observableArray([]);
        self.selected_system = ko.observable(null);
        self.selected_element = ko.observable();

        self.mapping = {
            systems: {
                key: function(data) {
                    return ko.utils.unwrapObservable(data.id);
                },
                create: function (options) {
                    console.log("create system", options.data);
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
                  console.log("got system data", data);

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
                  self.listener = ko.computed(self.send);
              });

        self.send = function () {
            var data = ko.mapping.toJS(self);
            console.log("sending", JSON.stringify(data));
            $.ajax({url: "/system", type: "POST",
                    data: JSON.stringify(data), contentType: "application/json",
                    success: function (data) {
                        //self.set(data);
                        console.log("got", data);
                        if (data.systems.length > 0) {
                            ko.mapping.fromJS(data.systems, self.mapping, self.systems);
                        }
                    }});
        };

        self.add_system = function () {
            var systemdata = create(schemas, "system", "Free");
            systemdata.elements = [];
            systemdata.sources = [];
            var system = new OpticalSystem(systemdata);
            self.systems.push(system);
            self.selected_system(system);
        };

        self.select_system = function (system) {
            self.selected_element(null);
            self.selected_system(system);
        };

        self.select_element = function (element, system) {
            console.log("select", element, system);
            self.selected_system(system);
            self.selected_element(element);
        };

    };

    ko.applyBindings(new MainViewModel());
})();