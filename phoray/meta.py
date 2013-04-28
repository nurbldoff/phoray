import os
from pprint import pprint
from inspect import getmembers, isclass, getmro
from imp import find_module, load_module
from operator import itemgetter
from collections import OrderedDict

import system, element, surface, source
import util


# Some plugin stuff, not really ready for use
PLUGIN_DIR = "plugins"
plugins = [os.path.splitext(mod)[0]
           for mod in os.listdir(PLUGIN_DIR) if mod.endswith(".py")]
plugin_classes = [
    #(plugin + "." + name, cls)
    (name, cls) for plugin, module
    in ((plug, load_module(plug, *find_module(plug, [PLUGIN_DIR])))
        for plug in sorted(plugins))
    for name, cls in sorted(getmembers(module, isclass), key=itemgetter(0))]


# List all the things we have available, by checking which classes
# inherit the base classes.
def get_classes(module, baseclass):
    return OrderedDict((name, cls) for name, cls
                       in sorted(getmembers(module, isclass),
                                 key=itemgetter(0)) + plugin_classes
                       if baseclass in getmro(cls)[1:])

classes = dict(System=get_classes(system, system.OpticalSystem),
               Element=get_classes(element, element.Element),
               Surface=get_classes(surface, surface.Surface),
               Source=get_classes(source, source.Source))

schemas = dict((id(cls), util.signature(cls))
               for _, clss in classes.items()
               for name, cls in clss.items())


def create_system(spec={}):
    """Create a System instance from specifications."""
    cls = classes["System"][spec.get("type", "Free")]
    args = spec.get("args", {})
    args["elements"] = [create_element(elspec)
                        for elspec in args.get("elements", [])]
    args["sources"] = [create_source(srcspec)
                       for srcspec in args.get("sources", [])]
    pprint(args)
    system = cls(_id=spec.get("_id"), **args)
    print "system.elements", system.elements
    return system


def create_geometry(spec={}):
    """Create a Surface instance from specifications."""
    cls = classes["Surface"].get(spec.get("type", "Plane"))
    geometry = cls(**spec.get("args", {}))
    return geometry


def create_element(spec={}):
    """Create an Element instance from specifications."""
    cls = classes["Element"][spec.get("type", "Mirror")]
    args = spec.get("args", {})
    geo = create_geometry(args.get("geometry", {}))
    args["geometry"] = geo
    element = cls(_id=spec.get("_id"), **args)
    return element


def create_source(spec={}):
    """Create a Source instance from specifications."""
    cls = classes["Source"].get(spec.get("type", "GaussianSource"))
    source = cls(_id=spec.get("_id"), **spec.get("args", {}))
    return source
