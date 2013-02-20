from pprint import pprint
from inspect import getmembers, isclass, getmro
from imp import find_module, load_module
from operator import itemgetter
import json
import copy
import os
from collections import OrderedDict

from bottle import get, post, request, run, static_file, route
from phoray import system, element, surface, source
import util

optical_systems = []

# Figure out what plugins are available

PLUGIN_DIR = "plugins"
plugins = [os.path.splitext(mod)[0]
           for mod in os.listdir(PLUGIN_DIR) if mod.endswith(".py")]
plugin_classes = [
    #(plugin + "." + name, cls)
    (name, cls)
    for plugin, module
    in ((plug, load_module(plug, *find_module(plug, [PLUGIN_DIR])))
        for plug in sorted(plugins))
    for name, cls in sorted(getmembers(module, isclass), key=itemgetter(0))]

# List all the things we have available, by checking which classes
# inherit the different base classes.

system_classes = OrderedDict((name, cls) for name, cls
                             in sorted(getmembers(system, isclass),
                                       key=itemgetter(0)) + plugin_classes
                             if system.OpticalSystem in getmro(cls)[1:])
element_classes = OrderedDict((name, cls) for name, cls
                              in sorted(getmembers(element, isclass),
                                        key=itemgetter(0)) + plugin_classes
                              if element.Element in getmro(cls)[1:])
surface_classes = OrderedDict((name, cls) for name, cls
                              in sorted(getmembers(surface, isclass),
                                        key=itemgetter(0)) + plugin_classes
                              if surface.Surface in getmro(cls)[1:])
source_classes = OrderedDict((name, cls) for name, cls
                             in sorted(getmembers(source, isclass),
                                       key=itemgetter(0)) + plugin_classes
                             if source.Source in getmro(cls)[1:])

# Find out the argument types for each class.

schemas = dict(System=OrderedDict((name, {})
                                  for name, cls in system_classes.items()),
               Surface=OrderedDict((name, util.signature(cls))
                                   for name, cls in surface_classes.items()),
               Element=OrderedDict((name, util.signature(cls))
                                   for name, cls in element_classes.items()),
               Source=OrderedDict((name, util.signature(cls))
                                  for name, cls in source_classes.items()))


def create_geometry(spec):
    cls = surface_classes.get(spec["type"])
    args = dict((name, prop) for name, prop in spec["args"].items())
    geometry = cls(**args)
    geometry.id = spec["id"]
    return geometry


def create_element(spec):
    cls = element_classes[spec["type"]]
    args = dict((name, prop) for name, prop in spec["args"].items())
    args["geometry"] = create_geometry(args["geometry"])
    element = cls(**args)
    element.id = spec["id"]
    return element


def create_source(spec):
    print "source spec"
    pprint(spec)
    cls = source_classes.get(spec["type"])
    args = dict((name, prop) for name, prop in spec["args"].items())
    source = cls(**args)
    source.id = spec["id"]
    return source


@route('/')
def staticindex():
    return static_file('index.html', root='ui')


@route('/<filepath:path>')
def staticpath(filepath):
    return static_file(filepath, root='ui')


@get('/schema')
def get_schema():

    return {"system": schemas["System"],
            "geometry": schemas["Surface"],
            "element": schemas["Element"],
            "source": schemas["Source"]}


@post('/system')
def define_system():
    """Define some elements to make up the optical system."""

    global optical_systems
    optical_systems = []

    query = request.json
    specs = copy.deepcopy(query)

    pprint(specs)

    for spec in specs["systems"]:
        sys_class = system_classes[spec["type"]]
        system = sys_class()
        system.id = spec["id"]

        for ele_spec in spec["elements"]:
            emt = create_element(ele_spec)
            system.elements.append(emt)

        for src_spec in spec["sources"]:
            try:
                src = create_source(src_spec)
                system.sources.append(src)
            except KeyError as e:
                print "Error:", str(e)

        system.update()
        optical_systems.append(system)

    # Figure out if anything has changed from the recieved spec
    diff = []
    for i, sys in enumerate(optical_systems):
        qsys = query["systems"][i]
        element_diffs = [util.dictdiff(qsys["elements"][j],
                                       util.object_to_dict(el, schemas))
                         for j, el in enumerate(sys.elements)]
        source_diffs = [util.dictdiff(qsys["sources"][j],
                                      util.object_to_dict(so, schemas))
                        for j, so in enumerate(sys.sources)]
        system_diff = {}
        if any(element_diffs):
            system_diff["elements"] = element_diffs
        if any(source_diffs):
            system_diff["sources"] = source_diffs
        diff.append(system_diff)

    print "diff"
    pprint(diff)
    if any(diff):
        return get_system()
    else:
        return dict()
    #return dict(systems=diff)


@post('/add_system')
def add_system():
    query = request.json
    cls = system_classes[query["type"]]
    where = optical_systems
    where.insert(query["index"], cls())
    return get_system()


@post('/add_element')
def add_element():
    query = request.json
    cls = element_classes[query["type"]]
    where = optical_systems[query["system"]].elements
    where.insert(query["index"], cls())
    return get_system()


@post('/add_source')
def add_source():
    query = request.json
    cls = source_classes[query["type"]]
    where = optical_systems[query["system"]].sources
    where.insert(query["index"], cls())
    return get_system()


@get('/mesh')
def get_mesh():
    """Return a mesh representation of an element."""
    query = request.query
    spec = json.loads(query["geometry"])
    geo = create_geometry(spec)
    verts, faces = geo.mesh(int(query.resolution))
    return {"verts": verts, "faces": faces}


@get('/system')
def get_system():
    """Return the current defined system."""
    systems = []
    for system in optical_systems:
        elements = []
        sources = []
        for element in system.elements:
            elements.append(util.object_to_dict(element, schemas))
        for source in system.sources:
            sources.append(util.object_to_dict(source, schemas))
        sysdict = util.system_to_dict(system, schemas)
        systems.append(sysdict)
    return dict(systems=systems)


@get('/axis')
def axis():
    """Return the guide axis."""
    return {"axis": [dict(x=pt.x, y=pt.y, z=pt.z)
                     for pt in optical_systems[0].axis()]}


@get('/trace')
def trace():
    """Trace the paths of a number of rays through a system."""
    query = request.query
    system = optical_systems[int(query.system)]

    n = int(query.n)  # number of rays to trace
    result = {}

    for i, source in enumerate(system.sources):
        traces = []
        for ray in source.generate(n):
            tmp = [tuple(r.endpoint) for r in system.propagate(ray, i)]
            if r.direction is None:
                pass
            else:
                tmp.append(tuple(r.endpoint + r.direction * 1))
            traces.append(tmp)
        result[i] = traces

    return {"traces": result}


@get('/footprint')
def footprint():
    """Return the current traced footprint for the given element."""
    query = request.query
    sys_n = int(query.system)
    ele_n = int(query.element)  # the chosen element

    return {"footprint": optical_systems[sys_n].elements[ele_n].footprint}


# Start the server
run(host='localhost', port=8080, debug=True, reloader=True)
