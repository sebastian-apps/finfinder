import json



def json2dict(json_data):
    """ convert JSON to dictionary """
    return {key:set(vals) for key, vals in json_data.items()}


def dict2json(dict):
    """ convert dictionary to JSON """
    return json.dumps(dict, cls=SetEncoder, indent=4)


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)



def write_jsonfile(dict, filename):
    """
    Good practice: give the file .json extension
    To do: Check if file already exists
    """
    data = dict2json(dict)
    f = open(filename,"w")
    f.write(data)
    f.close()
    print(f"{filename} saved.")



def read_jsonfile(filename):
    with open(filename) as json_file:
        if json_file is None:
            return '-1'
        else:
            return json.load(json_file)



def pretty_print(dict):
    """
    Makes legible by converting to json and serializing
    Warning: by converting to JSON, sets will be represented as lists
    """
    print(json.dumps(dict, cls=SetEncoder, indent=4))  # option: sort_keys=True
