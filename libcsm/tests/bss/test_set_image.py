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

from click.testing import CliRunner
from libcsm.bss import set_image
from libcsm.hsm import xnames
import traceback

@mock.patch('libcsm.api.Auth', spec=True)
@mock.patch('libcsm.bss.api.API.set_bss_image', spec=True)
@mock.patch('libcsm.s3.images.get_s3_image_info', spec=True)
@mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
class TestSetImage:

    """
    Tests for the bss set image main function.
    """

    def test_set_image(self, *_) -> None:
        """
        Verify clean run, this mocks every function used.
        """
        cli_runner = CliRunner()
        result = cli_runner.invoke(set_image.main, ["--image-id", "image123", "--xnames", "xname1"])
        traceback.print_exception(*result.exc_info)
        assert result.exit_code == 0

    def test_set_image_bad_inputs(self, *_) -> None:
        """
        Verify invalid inputs raises exceptions, this mocks every function used.
        """
        cli_runner = CliRunner()
        result = cli_runner.invoke(set_image.main, ["--image-id", "image123"])
        assert result.exit_code == 1

    @mock.patch('libcsm.hsm.xnames.get_by_role_subrole', spec=True)
    def test_set_image_with_role_subrole(self, mock_role_subrole, *_) -> None:
        """
        Verify clean run with hsm_role_subrole provided.
        """
        #with mock.patch.object(xnames, 'get_by_role_subrole', return_value=["xname1", "xname2"]):
        mock_role_subrole.return_value = ["xname1", "xname2"]
        cli_runner = CliRunner()
        result = cli_runner.invoke(set_image.main, ["--image-id", "image123", "--hsm-role-subrole", "Management_Storage"])
        #assert result.exit_code == 0
        traceback.print_exception(*result.exc_info)
        assert not result.exception

    def test_set_image_with_bad_role_subrole(self, *_) -> None:
        """
        Verify invalid run with bad hsm_role_subrole provided.
        """
        cli_runner = CliRunner()
        result = cli_runner.invoke(set_image.main, ["--image-id", "image123", "--hsm-role-subrole", "Management_BAD"])
        traceback.print_exception(*result.exc_info)
        assert result.exit_code == 1
