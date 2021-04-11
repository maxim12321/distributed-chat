from typing import Optional, Callable, Dict, Any
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
                data = file.read()
                dict_data = dict()
                if len(data) != 0:
                    dict_data = json.loads(data, object_hook=object_hook)
                file.close()
                return dict_data
        except FileNotFoundError:
            return dict()

    def _save_dict_in_file(self, data_dict: dict) -> None:
        with open(self.FILE_NAME, "w+") as file:
            json.dump(data_dict, file, indent=constants.INDENT)

    def _delete_old_object(self, data_dict: dict, tag_array: str, tag_object: str) -> None:
        for index, list_value in enumerate(data_dict[tag_array]):
            if list(list_value.keys())[0] == tag_object:
                data_dict[tag_array].pop(index)
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

    def load_object(self, tag: str, load_object: object) -> None:
        dict_data = self._load_json_file(json_decoder.decode)
        load_object.load_from_dict(dict_data[tag])

    def load_array_of_objects(self, tag_array: str, load_object: object) -> list:
        dict_data = self._load_json_file(json_decoder.decode)
        list_data = list()
        for list_value in dict_data[tag_array]:
            load_object.load_from_dict(list_value)
            element = copy.deepcopy(load_object)
            list_data.append(element)
        return list_data

    def save_object_to_array(self, tag_array: str, tag_object: str, object_to_save: object) -> None:
        data_dict = self._load_json_file()
        serialized_object = self._get_serialized_object(object_to_save)

        if tag_array not in data_dict.keys():
            data_dict[tag_array] = list()
        self._delete_old_object(data_dict, tag_array, tag_object)
        data_dict[tag_array].append({tag_object: serialized_object})

        self._save_dict_in_file(data_dict)

    def save_object(self, tag: str, object_to_save: object) -> None:
        data_dict = self._load_json_file()
        serialized_object = self._get_serialized_object(object_to_save)

        if tag in list(data_dict.keys()):
            data_dict.pop(tag)
        data_dict[tag] = serialized_object

        self._save_dict_in_file(data_dict)
