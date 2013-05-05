import copy
import json
from pprint import pprint
import os
import time
from multiprocessing import Pool
from Queue import Queue, Empty

import tornado.ioloop
import tornado.web
from sockjs.tornado import SockJSConnection, SockJSRouter, proto

from phoray.meta import (classes, schemas, create_system, create_element,
                         create_source, create_geometry)
import util


class BaseHandler(tornado.web.RequestHandler):

    pass

    # def initialize(self, data, trace_conn, pool, queue):
    #     self.data = data
    #     self.trace_conn = trace_conn
    #     self.pool = pool
    #     self.queue = queue


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
                             for s in data])

    def get(self):
        self.write(self._get_system())

    def post(self):
        data[:] = []
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


def _trace(system, n):
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
    return result


class TraceHandler(BaseHandler):

    """Trace the paths of a number of rays through a system."""

    def get(self):
        system = data[int(self.get_argument("system"))]
        #result = {}
        n = int(self.get_argument("n"))  # number of rays to trace

        result = pool.apply(_trace, (system, n))
        print result
        queue.put(result)


class TraceConnection(SockJSConnection):
    def on_open(self, info):
        pass
        #self.loop = tornado.ioloop.PeriodicCallback(self._send_stats,
        #1000)
        #ioloop.add_callback(self._send_stats)
        #self.loop.start()
        #pass

    def on_message(self, message):
        print
        print "on_message:", message
        print
        system = data[int(message.get("system"))]
        #result = {}
        n = int(message.get("n"))  # number of rays to trace

        pool.apply_async(_trace, (system, n), callback=self._send_result)

    def on_close(self):
        pass  #self.loop.stop()

    def _send_result(self, result):
        print "result:", result
        self.send(result)

    def _send_stats(self, result):
        #data = protoa.json_encode(BroadcastRouter.stats.dump())
        try:
            res = queue.get(block=False)
            print "   ### trace result:", res
            print
            self.send(res)
        except Empty:
            pass
        ioloop.add_timeout(time.time() + 0.1, self._send_stats)


class Application(tornado.web.Application):
    def __init__(self):
        #args = dict(data=data, trace_conn=trace_router, pool=pool, queue=queue)
        handlers = [
            (r'/index.html', MainHandler),
            (r'/schema', SchemaHandler),
            (r'/system', SystemHandler),
            (r'/create', CreateHandler),
            (r'/mesh', MeshHandler),
            (r'/trace', TraceHandler)
            ] + trace_router.urls
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "ui/"),
            static_path=os.path.join(os.path.dirname(__file__), "ui/"),
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    data = []
    pool = Pool(processes=2)
    queue = Queue()
    trace_router = SockJSRouter(SockJSConnection, '/traceconn')
    app = Application()
    app.listen(8080)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.start()
