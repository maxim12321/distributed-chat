from urllib import request
from typing import Dict, List, Tuple
import hashlib

from src.byte_message_type import ByteMessageType
from src.message_builders.message_builder import MessageBuilder
from src.message_parsers.container import Container
from src.message_parsers.message_parser import MessageParser


class ImageManager:
    def __init__(self):
        self.images: Dict[str, bytes] = dict()

    def save_images(self, image_paths: List[str]) -> List[str]:
        images_full_names = []

        for path in image_paths:
            mime_type = path[path.index(':') + 1:path.index(';')]
            print(mime_type)
            try:
                with request.urlopen(path) as image_file:
                    image_data = image_file.read()
                    image_hash = hashlib.sha256(image_data).hexdigest()

                    image_data = MessageBuilder.builder() \
                        .append_string(mime_type) \
                        .append_bytes(image_data) \
                        .build()

                    self.images[image_hash] = image_data
                    images_full_names.append(image_hash)

            except FileExistsError:
                pass

        return images_full_names

    def handle_message(self, message: bytes) -> None:
        image_hash: Container[str] = Container()
        image_bytes: Container[bytes] = Container()

        MessageParser.parser(message) \
            .append_string(image_hash) \
            .append_bytes(image_bytes) \
            .parse()

        print(f"New image added! Hash is {image_hash.get()}")
        self.images[image_hash.get()] = image_bytes.get()

    def build_image_message(self, image_hash: str) -> bytes:
        return MessageBuilder.builder() \
            .append_type(ByteMessageType.IMAGE_MESSAGE) \
            .append_string(image_hash) \
            .append_bytes(self.images[image_hash]) \
            .build()

    def get_image(self, image_hash: str) -> Tuple[str, bytes]:
        mime_type: Container[str] = Container()
        data: Container[bytes] = Container()

        MessageParser.parser(self.images[image_hash]) \
            .append_string(mime_type) \
            .append_bytes(data) \
            .parse()

        return mime_type.get(), data.get()

    def get_images(self, full_image_names: List[str]) -> List[bytes]:
        images_content = []
        for image_name_bytes in full_image_names:
            images_content.append(self.images[image_name_bytes])
        return images_content
