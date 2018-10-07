import json


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def write_json_to_shm(data, filename):
    with open('/dev/shm/' + filename, 'w') as f:
        json.dump(data, f)


def read_json_from_shm(filename):
    with open('/dev/shm/' + filename, 'r') as f:
        result = json.load(f)
    return result
