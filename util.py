from collections import OrderedDict
import inspect

from phoray import surface, element, source
from phoray.minivec import Vec


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
    print objkind, objtype
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
    if isinstance(attr, Vec):
        x, y, z = attr
        return dict(type="position", value=dict(x=x, y=y, z=z))
    elif isinstance(attr, surface.Surface):
        return dict(type="geometry", value=object_to_dict(attr, schema))
    else:
        return dict(type="number", value=attr)


def signature(cls):
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
            if argtype == Vec:
                argtype = "position"
                value = dict(x=value.x, y=value.y, z=value.z)
            elif argtype == surface.Surface:
                argtype = "geometry"
                value = None
            elif argtype in (int, float):
                argtype = "number"
            signature[arg] = dict(type=str(argtype), value=value)
    return signature
