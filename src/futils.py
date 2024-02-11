import json


def fexists(fname):
    try:
        f = open(fname, "r")
        f.close()
        return True
    except OSError:
       return False


def attempt_load_file(filename):
    if not fexists(filename):
        print(f"No {filename} found.")
        return None
    try:
        with open(filename, "rb") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error while loading {filename}")
        return None
