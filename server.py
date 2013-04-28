import copy
import json
from pprint import pprint

from bottle import get, post, request, run, static_file, route

from phoray.meta import (classes, schemas, create_system, create_element,
                         create_source, create_geometry)
#from phoray.phoray import current_id
import util


data = []


# == Route callbacks ===

@route('/')
def staticindex():
    return static_file('index.html', root='ui')


@route('/<filepath:path>')
def staticpath(filepath):
    return static_file(filepath, root='ui')


@get('/schema')
def get_schema():
    pprint(schemas)
    return dict((kind, dict((type, schemas[id(cls)])
                            for type, cls in clss.items()))
                for kind, clss in classes.items())


@post('/system')
def define_system():
    data[:] = []

    query = request.json
    spec = copy.deepcopy(query)

    for s in spec["systems"]:
        data.append(create_system(s))

    diff = [util.dictdiff(query["systems"][i],
                          util.object_to_dict(data[i], schemas))
            for i in range(len(data))]
    print "diff: ",
    pprint(diff)
    if len(diff) and diff[0]:
        return get_system()


@get('/system')
def get_system():
    return dict(systems=[util.object_to_dict(s, schemas) for s in data])


@get('/create')
def create():
    query = request.query
    kind = query.what.lower()
    if kind == "system":
        what = create_system(query)
    elif kind == "element":
        what = create_element(query)
    elif kind == "source":
        what = create_source(query)
    return util.object_to_dict(what, schemas)


@get('/mesh')
def get_mesh():
    """Return a mesh representation of an element."""
    query = request.query
    spec = json.loads(query["geometry"])
    geo = create_geometry(spec)
    verts, faces = geo.mesh(int(query.resolution))
    return {"verts": verts, "faces": faces}


@get('/trace')
def trace():
    """Trace the paths of a number of rays through a system."""
    query = request.query
    system = data[int(query.system)]

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
    sys_n = int(query.system)   # the containing system's index
    ele_n = int(query.element)  # the chosen element's index

    return {"footprint": data[sys_n].elements[ele_n].footprint}


# Start the server
run(host='localhost', port=8080, debug=True, reloader=True)
