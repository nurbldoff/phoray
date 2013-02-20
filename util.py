from collections import OrderedDict
import inspect

from phoray import surface, element, source
from phoray.minivec import Vec
from phoray import Length, Position, Rotation


def list_to_dict(l):
    return OrderedDict(zip(map(str, range(len(l))), l))


def dict_to_list(d):
    indexes = d.keys()
    l = []
    for i in range(max(indexes) + 1):
        l.append(d[i] if d[i] else {})
    return l


def dictdiff(d1, d2):
    c = {}
    for k in d2:
        if k not in d1:
            c[k] = d2[k]
            continue
        if d2[k] != d1[k]:
            if not (isinstance(d2[k], dict) or isinstance(d2[k], list)):
                c[k] = d2[k]
            else:
                if type(d1[k]) != type(d2[k]):
                    c[k] = d2[k]
                    continue
                else:
                    if isinstance(d2[k], dict):
                        c[k] = dictdiff(d1[k], d2[k])
                        continue
                    elif isinstance(d2[k], list):
                        c[k] = dict_to_list(dictdiff(list_to_dict(d1[k]),
                                                     list_to_dict(d2[k])))
    return c


def object_to_dict(obj, schema):
    objtype = obj.__class__.__name__
    objkind = [kind.__name__ for kind in (surface.Surface, element.Element,
                                          source.Source)
               if isinstance(obj, kind)][0]
    objdict = dict(type=objtype, args={})
    for name in schema[objkind][objtype]:
        value = getattr(obj, name)
        objdict["args"][name] = convert_attr(value, schema)
    objdict["id"] = obj.id
    return objdict


def system_to_dict(obj, schemas):
    schema = schemas["System"]
    objdict = dict(type=obj.__class__.__name__, args={})
    for name in schema[objdict["type"]]:
        value = getattr(obj, name)
        objdict["args"][name] = convert_attr(value, schema)
    objdict["elements"] = [object_to_dict(el, schemas) for el in obj.elements]
    objdict["sources"] = [object_to_dict(so, schemas) for so in obj.sources]
    objdict["id"] = obj.id
    return objdict


def convert_attr(attr, schema):
    print "convert attr", attr, type(attr)
    if isinstance(attr, Vec):
        return attr.dict()
    elif isinstance(attr, surface.Surface):
        return object_to_dict(attr, schema)
    else:
        return attr


def signature(cls):
    """Takes a class and tries to figure out the types of its arguments.

    TODO: not clean. Should be more explicit about argument types.
    """

    signature = OrderedDict()
    bases = inspect.getmro(cls)
    for base in (bases[:-1]):  # skip the object class
        spec = inspect.getargspec(base.__init__)
        if len(spec.args[1:]) != len(spec.defaults):
            print ("The init function for %s is missing default arguments!" %
                   cls.__name__)
            return None
        for i, arg in enumerate(spec.args[1:]):
            value = spec.defaults[i]
            #print "value", value
            argtype = type(value)
            if argtype in (Vec, Position):
                argtype = "position"
                value = value.dict()
            elif argtype == surface.Surface:
                argtype = "geometry"
                value = None
            elif argtype == Length:
                argtype = "length"
            elif argtype == int:
                argtype == "integer"
            elif argtype == float:
                argtype = "number"
            elif argtype == str:
                argtype = "string"
            signature[arg] = dict(type=str(argtype), value=value)
    return signature
