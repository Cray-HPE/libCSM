#
#  MIT License
#
#  (C) Copyright 2023 Hewlett Packard Enterprise Development LP
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#
"""
Function to return ``rootfs``, ``kernel``, and the ``initrd`` image path given an image ID.
"""

import json
from libcsm.s3 import s3object


class ImageFormatException(Exception):
    """
    An exception for problems getting "initrd", "kernel", "rootfs"
    image paths from an image in S3.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


def get_s3_image_info(bucket_name, image_id, endpoint_url) -> dict:
    """
    Retrieve the initrd, rootfs, and kernel image for an S3 bucket and image ID.

    This returns a dictionary

    .. code-block:: json

        {
            "rootfs": "<rootfs_image_path>",
            "kernel": "<kernal_image_path>",
            "initrd": "<initrd_image_path>"
        }

    :param bucket_name: Name of bucket.
    :param image_id: ID of image.
    :param endpoint_url: S3 endpoint.
    :raises ImageFormatException: When an image is not found.
    :returns: Dictionary of images.
    """
    image_manifest = image_id + "/manifest.json"
    image_object = s3object.S3Object(bucket_name, image_manifest)
    s3_object = image_object.get_object(endpoint_url)
    object_json = json.loads(s3_object['Body'].read())
    images_json = object_json['artifacts']

    image_dict = {}
    for image_type in ["initrd", "kernel", "rootfs"]:
        for image in images_json:
            if image_type in image['type']:
                image_dict[image_type] = image['link']['path']
                break
        try:
            if image_dict[image_type] is None:
                raise ImageFormatException(f"ERROR could not find image for {image_type}")
        except Exception as exc:
            raise ImageFormatException(f"ERROR could not find image for {image_type}") from exc

    print("Using images: ", image_dict)
    return image_dict
