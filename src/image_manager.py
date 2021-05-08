from typing import Dict, List
import hashlib


class ImageManager:
    def __init__(self):
        self.images: Dict[str, bytes] = dict()

    def save_images(self, image_paths: List[str]) -> List[str]:
        images_full_names = []

        for paths in image_paths:
            try:
                with open(paths, "rb") as image_file:
                    image_data = image_file.read()
                    image_hash = hashlib.sha256(image_data).hexdigest()

                    self.images[image_hash] = image_data
                    images_full_names.append(image_hash)

            except FileExistsError:
                pass

        return images_full_names

    def get_images(self, full_image_names: List[str]) -> List[bytes]:
        images_content = []
        for image_name_bytes in full_image_names:
            images_content.append(self.images[image_name_bytes])
        return images_content
