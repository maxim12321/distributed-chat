from typing import Optional, Callable, Dict, Any
from serializable import Serializable
import constants
import json_decoder
import copy
import json


class Preferences:
    def __init__(self):
        self.FILE_NAME = "../preferences.json"

    def _load_json_file(self, object_hook: Optional[Callable[[Dict[Any, Any]], Any]] = None) -> dict:
        try:
            with open(self.FILE_NAME, "r") as file:
                return json.loads(file.read(), object_hook=object_hook)
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()

    def _save_dict_to_file(self, data_dict: dict) -> None:
        with open(self.FILE_NAME, "w+") as file:
            json.dump(data_dict, file, indent=constants.INDENT)

    def _delete_old_object(self, data_dict: dict, array_tag: str, object_tag: str) -> None:
        for index, list_value in enumerate(data_dict[array_tag]):
            if list(list_value.keys())[0] == object_tag:
                data_dict[array_tag].pop(index)
                break

    def _is_primitive(self, obj: object) -> bool:
        return isinstance(obj, (float, int, str, bool))

    def _get_serialized_object(self, object_to_save: object) -> object:
        serialized_object = object_to_save
        if isinstance(object_to_save, bytes):
            serialized_object = constants.bytes_to_string(object_to_save)
        if not self._is_primitive(object_to_save):
            serialized_object = dict(object_to_save)
        return serialized_object

    def load_primitive_type(self, tag: str) -> object:
        dict_data = self._load_json_file()
        return dict_data[tag]

    def load_object(self, tag: str, load_object: Serializable) -> None:
        dict_data = self._load_json_file(json_decoder.decode)
        load_object.load_from_dict(dict_data[tag])

    def load_array_of_objects(self, array_tag: str, load_object: Serializable) -> list:
        dict_data = self._load_json_file(json_decoder.decode)
        list_data = list()
        for list_value in dict_data[array_tag]:
            load_object.load_from_dict(list_value)
            element = copy.deepcopy(load_object)
            list_data.append(element)
        return list_data

    def save_object_to_array(self, array_tag: str, object_tag: str, object_to_save: object) -> None:
        data_dict = self._load_json_file()
        serialized_object = self._get_serialized_object(object_to_save)
        if array_tag not in data_dict.keys():
            data_dict[array_tag] = list()
        self._delete_old_object(data_dict, array_tag, object_tag)
        data_dict[array_tag].append({object_tag: serialized_object})

        self._save_dict_to_file(data_dict)

    def save_object(self, tag: str, object_to_save: object) -> None:
        data_dict = self._load_json_file()
        serialized_object = self._get_serialized_object(object_to_save)

        if tag in data_dict.keys():
            data_dict.pop(tag)
        data_dict[tag] = serialized_object

        self._save_dict_to_file(data_dict)
