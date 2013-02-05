from pprint import pprint
import inspect
import json
import copy
import pyclbr

from bottle import get, post, request, run, static_file, route
from phoray import system, element, surface, source
import util

optical_systems = []


# List all the things we have available, by listing classes that
# inherit the different base classes.

system_classes = dict((name, obj)
                      for name, obj in inspect.getmembers(system)
                      if inspect.isclass(obj))
element_classes = dict((name, obj)
                       for name, obj in inspect.getmembers(element)
                       if inspect.isclass(obj) and
                       element.Element in inspect.getmro(obj)[1:])
surface_classes = dict((name, obj)
                       for name, obj in inspect.getmembers(surface)
                       if inspect.isclass(obj) and
                       surface.Surface in inspect.getmro(obj)[1:])
source_classes = dict((name, obj)
                      for name, obj in inspect.getmembers(source)
                      if inspect.isclass(obj) and
                      source.Source in inspect.getmro(obj)[1:])


# Find out the argument types for each class, by looking at the default
# arguments defined.

schemas = dict(System=dict((name, cls.schema)
                           for name, cls in system_classes.items()
                           if hasattr(cls, "schema")),  # update this too
               Surface=dict((name, util.signature(cls))
                            for name, cls in surface_classes.items()),
               Element=dict((name, util.signature(cls))
                            for name, cls in element_classes.items()),
               Source=dict((name, util.signature(cls))
                           for name, cls in source_classes.items()))


def _create_geometry(spec):
    cls = surface_classes.get(spec["type"])
    args = spec["args"]
    return cls(**args)


def _create_element(spec):
    cls = element_classes[spec["type"]]
    args = spec["args"]
    args["geometry"] = _create_geometry(args["geometry"])
    return cls(**args)


def _create_source(spec):
    cls = source_classes.get(spec["type"])
    args = spec["args"]
    return cls(**args)


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
    #pprint(query)
    specs = copy.deepcopy(query)

    for spec in specs["systems"]:
        pprint(spec)
        sys_class = system_classes[spec["type"]]
        system = sys_class()

        for ele_spec in spec["elements"]:
            emt = _create_element(ele_spec)
            system.elements.append(emt)
            print "Added element", ele_spec["type"]

        for src_spec in spec["sources"]:
            try:
                src = _create_source(src_spec)
                system.sources.append(src)
                print "Added source", src_spec["type"]
            except KeyError as e:
                print "Error:", str(e)

        system.update()
        optical_systems.append(system)

    # Figure out if anything has changed from the recieved spec
    diff = []
    for i, sys in enumerate(optical_systems):
        qsys = query["systems"][i]
        eldiffs = [util.dictdiff(qsys["elements"][j],
                                 util.object_to_dict(el, schemas))
                   for j, el in enumerate(sys.elements)]
        sodiffs = [util.dictdiff(qsys["sources"][j],
                                 util.object_to_dict(so, schemas))
                   for j, so in enumerate(sys.sources)]
        sysdiff = {}
        if any(eldiffs):
            sysdiff["elements"] = eldiffs
        if any(sodiffs):
            sysdiff["sources"] = sodiffs
        diff.append(sysdiff)

    # pprint([util.system_to_dict(system, system_schema)
    #         for i, system in enumerate(optical_systems)])
    pprint(diff)
    return {"systems": diff}


@get('/mesh')
def get_mesh():
    query = request.query
    print "mesh query", query["geometry"]
    spec = json.loads(query["geometry"])
    geo = _create_geometry(spec)
    verts, faces = geo.mesh(int(query.resolution))
    return {"verts": verts, "faces": faces}


@get('/system')
def get_system():
    systems = []
    for system in optical_systems:
        elements = []
        sources = []
        for element in system.elements:
            elements.append(util.object_to_dict(element, schemas))
        for source in system.sources:
            sources.append(util.object_to_dict(source, schemas))
        systems.append(dict(elements=elements, sources=sources))
    print "sending systems", systems
    return dict(systems=systems)


@get('/axis')
def axis():
    return {"axis": [dict(x=pt.x, y=pt.y, z=pt.z)
                     for pt in optical_systems[0].axis()]}


@get('/trace')
def trace():
    """Trace the paths of a number of rays through a system."""
    query = request.query
    n = int(query.n)  # number of rays to trace

    result = []

    for system in optical_systems:
        traces = system.trace(n)
        for trace in traces:
            step = []
            start = trace[0].endpoint
            for ray in trace:
                x, y, z = ray.endpoint
                step.append((x, y, z))
                print (ray.endpoint - start).length(),
                start = ray.endpoint
            end = ray.endpoint + ray.direction * 10
            print (end - start).length()
            step.append((end.x, end.y, end.z))
            result.append(step)
    return {"traces": result}


@get('/footprint')
def footprint():
    """Return the current traced footprint for the given element."""
    query = request.query
    n = int(query.n)  # the chosen element
    return {"footprint": optical_systems[0].elements[n].footprint}


# Start the server
run(host='localhost', port=8080, debug=True, reloader=True)
