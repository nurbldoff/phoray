import copy
import json
from pprint import pprint
import os

import tornado.ioloop
import tornado.web

from phoray.meta import (classes, schemas, create_system, create_element,
                         create_source, create_geometry)
import util


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self, data):
        self.data = data


class MainHandler(BaseHandler):

    def get(self):
        self.render("index.html")


class SchemaHandler(BaseHandler):

    """Get the signatures for all items."""

    def get(self):
        pprint(schemas)
        self.write(dict((kind, dict((type, schemas[id(cls)])
                                    for type, cls in clss.items()))
                        for kind, clss in classes.items()))


class SystemHandler(BaseHandler):

    """Operations on system data."""

    def _get_system(self):
        return dict(systems=[util.object_to_dict(s, schemas)
                             for s in self.data])

    def get(self):
        self.write(self._get_system())

    def post(self):
        self.data[:] = []
        query = json.loads(self.request.body)
        spec = copy.deepcopy(query)
        for s in spec["systems"]:
            data.append(create_system(s))

        diff = [util.dictdiff(query["systems"][i],
                              util.object_to_dict(data[i], schemas))
                for i in range(len(data))]
        print "diff: ",
        pprint(diff)
        if len(diff) and diff[0]:
            self.write(self._get_system())


class CreateHandler(BaseHandler):

    """Create new items."""

    def get(self):
        kind = self.get_argument("what").lower()
        if kind == "system":
            what = create_system()
        elif kind == "element":
            what = create_element()
        elif kind == "source":
            what = create_source()

        self.write(util.object_to_dict(what, schemas))


class MeshHandler(BaseHandler):

    """Return a mesh representation of an element."""

    def get(self):
        geometry = json.loads(self.get_argument("geometry"))
        resolution = self.get_argument("resolution")
        geo = create_geometry(geometry)
        verts, faces = geo.mesh(int(resolution))

        self.write({"verts": verts, "faces": faces})


class TraceHandler(BaseHandler):

    """Trace the paths of a number of rays through a system."""

    def get(self):
        system = data[int(self.get_argument("system"))]

        n = int(self.get_argument("n"))  # number of rays to trace
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

        self.write({"traces": result})


class Application(tornado.web.Application):
    def __init__(self, data):
        args = dict(data=data)
        handlers = [
            (r'/index.html', MainHandler, args),
            (r'/schema', SchemaHandler, args),
            (r'/system', SystemHandler, args),
            (r'/create', CreateHandler, args),
            (r'/mesh', MeshHandler, args),
            (r'/trace', TraceHandler, args),
            ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "ui/"),
            static_path=os.path.join(os.path.dirname(__file__), "ui/"),
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    data = []
    app = Application(data)
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
