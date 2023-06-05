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
Testing geting image information from an image in s3.
"""

import json
import io
import pytest
import mock
from botocore.response import StreamingBody

from libcsm.s3 import images, s3object
from libcsm.s3.images import ImageFormatException

def mock_s3_object(mocked_images: dict) -> dict:
    """
    Mock s3 objects.
    """
    body_json = {
            'artifacts': mocked_images 
    }
    body_string = json.dumps(body_json).encode()
    body_stream = StreamingBody(
        io.BytesIO(body_string),
        len(body_string)
    )
    return {'Body': body_stream}

@mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
class TestGetS3ImageInfo:

    """
    Tests for the get_s3_image_info function.
    """

    @mock.patch('libcsm.s3.s3object.S3Object.get_object')
    def test_good_get_image_info(self, mock_get_object, *_) -> None:
        """
        Verify get_s3_image_info runs smoothly when a good repsonse is recieved from s3.
        """
        mock_get_object.return_value = 0
        mocked_images = [
            {"type" : "initrd", "link": {"path": "initrd_path"} },
            {"type" : "kernel", "link": {"path": "kernel_path"} },
            {"type" : "rootfs", "link": {"path": "rootfs_path"} },
        ]
        mock_object = mock_s3_object(mocked_images)
        with mock.patch.object(s3object.S3Object, 'get_object', \
            return_value=mock_object):
            image_dict = images.get_s3_image_info("bucket", "image", "info")
            assert image_dict['initrd'] == "initrd_path"
            assert image_dict['kernel'] == "kernel_path"
            assert image_dict['rootfs'] == "rootfs_path"

    @mock.patch('libcsm.s3.s3object.S3Object.get_object')
    def test_bad_get_image_info(self, mock_get_object, *_) -> None:
        """
        Verify get_s3_image_info fails when invalid image format is recieved.
        """
        mock_get_object.return_value = 0
        mocked_images = [
            {"type" : "XX-bad-XX", "link": {"path": "initrd_path"} },
            {"type" : "kernel", "link": {"path": "kernel_path"} },
            {"type" : "rootfs", "link": {"path": "rootfs_path"} },
        ]
        mock_object = mock_s3_object(mocked_images)
        with mock.patch.object(s3object.S3Object, 'get_object', \
            return_value=mock_object):
            with pytest.raises(ImageFormatException):
                images.get_s3_image_info("bucket", "image", "info")
