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

import json
import io
import pytest
import mock
from botocore.response import StreamingBody

from libcsm.s3 import images, s3object

class MockS3Object:
    """
    A mock for kubernetes.client.models.v1_secret.V1Secret
    """
    def __init__(self, mocked_images):
        body_json = {
                'artifacts': mocked_images 
        }

        body_string = json.dumps(body_json).encode()

        body_stream = StreamingBody(
            io.BytesIO(body_string),
            len(body_string)
        )

        self.mock_response = {'Body': body_stream}


class TestGetS3ImageInfo:

    """
    Tests for the get_s3_image_info function.
    """

    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    @mock.patch('libcsm.s3.s3object.S3Object.get_object')
    def test_good_get_image_info(self, mock_get_object, mock_verify_bucket_exists) -> None:
        """
        Verify get_s3_image_info runs smoothly when a good repsonse is recieved from .
        """
        mock_get_object.return_value = 0
        mocked_images = [ {"type" : "initrd", "link": {"path": "initrd_path"} },
                        {"type" : "kernel", "link": {"path": "kernel_path"} },
                        {"type" : "rootfs", "link": {"path": "rootfs_path"} }
                    ]
        mock_object = MockS3Object(mocked_images)
        with mock.patch.object(s3object.S3Object, 'get_object', return_value=mock_object.mock_response):
            image_dict = images.get_s3_image_info("bucket", "image", "info")
            assert image_dict['initrd'] == "initrd_path"
            assert image_dict['kernel'] == "kernel_path"
            assert image_dict['rootfs'] == "rootfs_path"

    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    @mock.patch('libcsm.s3.s3object.S3Object.get_object')
    def test_bad_get_image_info(self, mock_get_object, *_) -> None:
        """
        Verify get_s3_image_info runs smoothly.
        """
        mock_get_object.return_value = 0
        mocked_images = [ {"type" : "XX-bad-XX", "link": {"path": "initrd_path"} },
                        {"type" : "kernel", "link": {"path": "kernel_path"} },
                        {"type" : "rootfs", "link": {"path": "rootfs_path"} }
                    ]
        mock_object = MockS3Object(mocked_images)
        with mock.patch.object(s3object.S3Object, 'get_object', return_value=mock_object.mock_response):
            with pytest.raises(Exception):
                images.get_s3_image_info("bucket", "image", "info")
