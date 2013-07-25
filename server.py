import copy
import json
from pprint import pprint
from time import time

from numpy import isnan
from bottle import get, post, request, run, static_file, route

from meta import (classes, schemas, create_system, create_element,
                  create_source, create_geometry, create_frame)
import util


# == Route callbacks ===

@route('/')
def staticindex():
    return static_file('index.html', root='ui')


@route('/static/<filepath:path>')
def staticpath(filepath):
    return static_file(filepath, root='ui')


@get('/schema')
def get_schema():
    print("schema")
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
    print("diff: ",)
    pprint(diff)
    if len(diff) and diff[0]:
        return get_system()


@get('/system')
def get_system():
    return dict(systems=[util.object_to_dict(s, schemas) for s in data])


@get('/create')
def create():
    query = request.query
    print(dict(query))

    if query.base == "System":
        what = create_system(query)
    elif query.base == "Element":
        what = create_element(query)
    elif query.base == "Source":
        what = create_source(query)
    elif query.base == "Surface":
        what = create_geometry(query)
    elif query.base == "Frame":
        what = create_frame(query)
    result = util.object_to_dict(what, schemas)
    pprint(result)
    return result


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
    t0 = time()
    query = request.query
    system = data[int(query.system)]

    n = int(query.n)  # number of rays to trace
    traces = system.trace(n)

    # Format the footprint data for consumption by the UI.
    # Separates out the failed rays and add "dummies" for
    # non-terminated ones.
    result = []
    for trace in traces:
        succeeded = []
        failed = []
        tmp = dict(succeeded=succeeded, failed=failed)
        for i in range(n):
            tmp2 = []
            for j, tr in enumerate(trace):
                broke = False
                if isnan(tr.endpoints[i][0]):
                    tmp2.append(tuple(trace[j-1].endpoints[i] +
                                      trace[j-1].directions[i]))
                    broke = True
                    break
                else:
                    tmp2.append(tuple(tr.endpoints[i]))
            if broke:
                failed.append(tmp2)
            if not broke:
                tmp2.append(tuple(tr.endpoints[i] + tr.directions[i]))
                succeeded.append(tmp2)
        result.append(tmp)

    dt = time() - t0
    print("traced %d rays, took %f s." % (n, dt))
    return dict(traces=result, time=dt)


@get('/footprint')
def footprint():
    """Return the current traced footprint for the given element."""
    query = request.query
    sys_n = int(query.system)   # the containing system's index
    ele_n = int(query.element)  # the chosen element's index

    return {"footprint": data[sys_n].elements[ele_n].footprint}


if __name__ == "__main__":
    data = []
    # Start the server
    run(host='localhost', port=8080, debug=True, reloader=True)
