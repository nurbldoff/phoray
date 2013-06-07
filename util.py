from collections import OrderedDict
import inspect
from pprint import pprint

from phoray import surface, element, source
from phoray.minivec import Vec
from phoray import Length, Position, Rotation


def list_to_dict(l):
    return OrderedDict(zip(map(str, range(len(l))), l))


def dict_to_list(d):
    print "dict_to_list",
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
                        print d1[k], d2[k]
                        c[k] = dict_to_list(dictdiff(list_to_dict(d1[k]),
                                                     list_to_dict(d2[k])))
    return c


def object_to_dict(obj, schemas):
    objtype = obj.__class__.__name__
    objdict = dict(type=objtype, args={})
    schema = schemas[id(obj.__class__)]
    for name in schema:
        value = getattr(obj, name)
        print name, value
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
    print "convert attr", attr, type(attr)
    if isinstance(attr, Vec):
        return attr.dict()
    elif isinstance(attr, surface.Surface):
        return object_to_dict(attr, schemas)
    elif isinstance(attr, list):
        return [object_to_dict(item, schemas) for item in attr]
    else:
        return attr


def signature(cls):
    """Takes a class and tries to figure out the types of its arguments.

    TODO: This is horrible.
    """

    signature = OrderedDict()
    bases = inspect.getmro(cls)
    for base in (bases[:-1]):  # skip the object class
        spec = inspect.getargspec(base.__init__)
        print base.__name__
        if len(spec.args[1:]) != len(spec.defaults):
            print ("The init function for %s is missing default arguments!" %
                   cls.__name__)
            return None
        for i, arg in enumerate(spec.args[1:]):
            if not arg.startswith("_"):
                value = spec.defaults[i]
                argtype = type(value)
                print "value", value, "argtype", argtype
                if value is None:
                    continue
                if argtype in (Vec, Position):
                    argtype = "position"
                    value = value.dict()
                elif argtype == surface.Surface:
                    argtype = "geometry"
                    value = None
                elif argtype == Length:
                    argtype = "length"
                elif argtype == int:
                    argtype = "integer"
                elif argtype == float:
                    argtype = "number"
                elif argtype == str:
                    argtype = "string"
                elif argtype == list:
                    argtype = "list"
                signature[arg] = dict(type=str(argtype), value=value)
    return signature
