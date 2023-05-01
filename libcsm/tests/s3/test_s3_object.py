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
Tests for the ``api`` submodule.
"""
from urllib import request

import base64
import io
from dataclasses import dataclass
import pytest
from kubernetes import client
from urllib3.exceptions import MaxRetryError
from libcsm.s3 import s3_object
import mock

from libcsm import api

class TestS3Object:

    """
    Tests for s3_object functions.
    """
    @mock.patch('libcsm.s3.s3_object.run_command', autospec=True)
    def test_verify_bucket_exists(self, mock_run_command):
        mock_run_command.return_value.return_code = 0
        s3_object.verify_bucket_exists("bucket")

    @mock.patch('libcsm.s3.s3_object.run_command', autospec=True)
    def test_verify_bucket_exists_error(self, mock_run_command):
        mock_run_command.return_value.return_code = 3
        with pytest.raises(Exception):
            s3_object.verify_bucket_exists("bucket")

    @mock.patch('libcsm.s3.s3_object.run_command', autospec=True)
    def test_verify_object_owner(self, mock_run_command):
        mock_run_command.return_value.return_code = 0
        mock_run_command.return_value.stdout = '{"policy":{"owner":{"id":"test_id"}}}'
        assert "test_id" == s3_object.get_object_owner("bucket", "object")

    @mock.patch('libcsm.s3.s3_object.run_command', autospec=True)
    def test_verify_object_owner_error(self, mock_run_command):
        mock_run_command.return_value.return_code = 3
        mock_run_command.return_value.stdout = '{"policy":{"owner":{"id":"test_id"}}}'
        with pytest.raises(Exception):
            s3_object.get_object_owner("bucket", "object")

    @mock.patch('libcsm.s3.s3_object.run_command', autospec=True)
    def test_get_creds(self, mock_run_command):
        mock_run_command.return_value.return_code = 0
        mock_run_command.return_value.stdout = '{"keys":[{"access_key":"test_access", "secret_key":"test_secret"}]}'
        assert ("test_access", "test_secret") == s3_object.get_creds("owner")

    @mock.patch('libcsm.s3.s3_object.run_command', autospec=True)
    def test_get_creds_error(self, mock_run_command):
        mock_run_command.return_value.return_code = 1
        mock_run_command.return_value.stdout = '{"keys":[{"access_key":"test_access","secret_key":"test_secret"}]}'
        with pytest.raises(Exception):
            s3_object.get_creds("owner")
