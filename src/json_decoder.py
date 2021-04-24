import base64


def decode(data_dict: dict):
    if "__bytes__" in data_dict:
        return base64.b64decode(data_dict["bytes"])
    return data_dict
