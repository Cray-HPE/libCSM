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

from libcsm.s3 import s3object


class TestS3Object:

    """
    Tests for the s3object submodule.
    """
    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    def test_object(self, *_) -> None:
        """
        Verify s3object class is initialized.
        """
        obj = s3object.S3Object("a_bucket", "b_object")
        assert obj.bucket == "a_bucket"
        assert obj.object_name == "b_object"
        assert obj.owner is None
        assert obj._a_key is None
        assert obj._s_key is None

    @mock.patch('libcsm.s3.s3object.run_command', autospec=True)
    def test_object_good_bucket(self, mock_run_command) -> None:
        """
        Verify verify_bucket_exists runs smoothly.
        """
        mock_run_command.return_value.return_code = 0
        s3object.S3Object("a_bucket", "b_object")

    @mock.patch('libcsm.s3.s3object.run_command', autospec=True)
    def test_object_bad_bucket(self, mock_run_command) -> None:
        """
        Verify verify_bucket_exists raises exception when run_command has error.
        """
        mock_run_command.return_value.return_code = 2
        with pytest.raises(Exception):
            s3object.S3Object("a_bucket", "b_object")

    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    @mock.patch('libcsm.s3.s3object.run_command', autospec=True)
    def test_object_owner(self, mock_run_command, *_) -> None:
        """
        Verify get_object_owner runs smoothly.
        """
        obj = s3object.S3Object("a_bucket", "b_object")

        mock_run_command.return_value.return_code = 0
        mock_run_command.return_value.stdout = '{"policy": {"owner": {"id": "owner_id"}}}'
        obj.get_object_owner()
        assert obj.owner == "owner_id"

    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    @mock.patch('libcsm.s3.s3object.run_command', autospec=True)
    def test_object_bad_owner(self, mock_run_command, *_) -> None:
        """
        Verify get_object_owner raises exception when run_command has error.
        """
        obj = s3object.S3Object("a_bucket", "b_object")

        mock_run_command.return_value.return_code = 2
        mock_run_command.return_value.stdout = '{"policy": {"owner": {"id": "owner_id"}}}'
        with pytest.raises(Exception):
            obj.get_object_owner()

    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    @mock.patch('libcsm.s3.s3object.S3Object.get_object_owner')
    @mock.patch('libcsm.s3.s3object.run_command', autospec=True)
    def test_get_creds(self, mock_run_command, *_) -> None:
        """
        Verify get_creds runs smoothly.
        """
        obj = s3object.S3Object("a_bucket", "b_object")

        mock_run_command.return_value.return_code = 0
        mock_run_command.return_value.stdout = '{"keys":[{"access_key":"test_access", "secret_key":"test_secret"}]}'
        obj.get_creds()
        assert obj._a_key == "test_access"
        assert obj._s_key == "test_secret"

    @mock.patch('libcsm.s3.s3object.S3Object.verify_bucket_exists')
    @mock.patch('libcsm.s3.s3object.S3Object.get_object_owner')
    @mock.patch('libcsm.s3.s3object.run_command', autospec=True)
    def test_get_bad_creds(self, mock_run_command, *_) -> None:
        """
        Verify get_creds raises exception when run_command has error.
        """
        obj = s3object.S3Object("a_bucket", "b_object")

        mock_run_command.return_value.return_code = 3
        with pytest.raises(Exception):
            obj.get_creds()
