from collections import OrderedDict
import inspect
from pprint import pprint

import numpy as np

from phoray import surface, element, source, member
from phoray import Length, Position, Rotation


def list_to_dict(l):
    return OrderedDict(zip(map(str, range(len(l))), l))


def dict_to_list(d):
    pprint(d)
    indexes = d.keys()
    l = []
    if indexes:
        for i in range(int(max(indexes)) + 1):
            l.append(d[str(i)] if str(i) in d else {})
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


def object_to_dict(obj, schemas):
    objtype = obj.__class__.__name__
    objdict = dict(type=objtype, args={})
    schema = schemas[id(obj.__class__)]
    for name in schema:
        value = getattr(obj, name)
        objdict["args"][name] = convert_attr(value, schemas)
    if hasattr(obj, "_id"):
        objdict["_id"] = obj._id
    return objdict


def system_to_dict(obj, schemas, objtype=None):
    schema = schemas["System"]
    if objtype is None:
        objtype = obj.__class__.__name__
    objdict = dict(type=objtype, args={})
    for name in schema[objdict["type"]]:
        value = getattr(obj, name)
        objdict["args"][name] = convert_attr(value, schema)
    pprint(objdict)
    if hasattr(obj, "_id"):
        objdict["_id"] = obj._id
    objdict["elements"] = [object_to_dict(el, schemas) for el in obj.elements]
    objdict["sources"] = [object_to_dict(so, schemas) for so in obj.sources]
    return objdict


def convert_attr(attr, schemas):
    if isinstance(attr, surface.Surface):
        return object_to_dict(attr, schemas)
    elif isinstance(attr, list):
        return [object_to_dict(item, schemas) for item in attr]
    elif isinstance(attr, np.ndarray):
        return dict(x=float(attr[0]), y=float(attr[1]), z=float(attr[2]))
    else:
        return attr


def signature(cls):
    """Takes a class and tries to figure out the types of its arguments.

    TODO: This is horrible.
    """

    sig = OrderedDict()
    bases = inspect.getmro(cls)
    for base in (bases[:-1]):  # skip the object class
        spec = base.__init__.__annotations__
        print("spec", spec)
        # if len(spec.args[1:]) != len(spec.defaults):
        #     print("The init function for %s is missing default arguments!" %
        #           cls.__name__)
        #     return None
        for arg, annot in spec.items():
            argsubtype = None
            argtype = annot
            if not arg.startswith("_"):
                if argtype in (Position, np.ndarray, tuple):
                    argtype = "vector"
                elif type(argtype) == list:
                    if len(argtype) > 0:
                        argsubtype = argtype[0].__name__
                    argtype = "list"
                else:
                    argtype = argtype.__name__
                sig[arg] = dict(type=str(argtype))
                if argsubtype:
                    sig[arg]["subtype"] = argsubtype
    print()
    print("signature", cls.__name__)
    pprint(sig)
    print()
    return sig
