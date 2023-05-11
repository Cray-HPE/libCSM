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

import pytest
import mock

from libcsm.bss import set_image
from libcsm.hsm import xnames


class TestSetImage:

    """
    Tests for the bss set image main function.
    """
    @mock.patch('libcsm.api.Auth', spec=True)
    @mock.patch('libcsm.bss.api.API.set_bss_image', spec=True)
    @mock.patch('libcsm.s3.images.get_s3_image_info', spec=True)
    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    def test_set_image(self, *_) -> None:
        """
        Verify clean run, this mocks every function used.
        """
        with mock.patch("sys.argv", ["main", "--image_id", "image123", "--xname", "xname1"]):
            set_image.main()

    @mock.patch('libcsm.api.Auth', spec=True)
    @mock.patch('libcsm.bss.api.API.set_bss_image', spec=True)
    @mock.patch('libcsm.s3.images.get_s3_image_info', spec=True)
    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    def test_set_image_bad_inputs(self, *_) -> None:
        """
        Verify invalid inputs raises exceptions, this mocks every function used.
        """
        with mock.patch("sys.argv", ["main", "--image_id", "image123"]):
            with pytest.raises(SystemExit):
                set_image.main()

    @mock.patch('libcsm.api.Auth', spec=True)
    @mock.patch('libcsm.bss.api.API.set_bss_image', spec=True)
    @mock.patch('libcsm.s3.images.get_s3_image_info', spec=True)
    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    def test_set_image_with_role_subrole(self, *_) -> None:
        """
        Verify clean run with hsm_role_subrole provided.
        """
        with mock.patch.object(xnames, 'get_by_role_subrole', return_value=["xname1", "xname2"]):
            with mock.patch("sys.argv", ["main", "--image_id", "image123", "--hsm_role_subrole", "Management_Storage"]):
                set_image.main()

    @mock.patch('libcsm.api.Auth', spec=True)
    @mock.patch('libcsm.bss.api.API.set_bss_image', spec=True)
    @mock.patch('libcsm.s3.images.get_s3_image_info', spec=True)
    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    def test_set_image_with_bad_role_subrole(self, *_) -> None:
        """
        Verify invalid run with bad hsm_role_subrole provided.
        """
        with mock.patch("sys.argv", ["main", "--image_id", "image123", "--hsm_role_subrole", "Management_BAD"]):
            with pytest.raises(SystemExit):
                set_image.main()
