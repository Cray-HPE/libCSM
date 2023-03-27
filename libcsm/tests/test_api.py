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
Tests for the api submodule.
"""
import base64
import io

from dataclasses import dataclass
from urllib import request
import pytest

from kubernetes import client
from urllib3.exceptions import MaxRetryError
import mock
from libcsm import api


@dataclass()
class MockV1Secret:
    """
    A mock for kubernetes.client.models.v1_secret.V1Secret
    """
    id = b'foo-client'
    secret = b'2fb9d9ad-3333-2222-1111-000000000000'
    endpoint = b'https://example.com'
    data = {
        "client-id": base64.b64encode(id),
        "client-secret": base64.b64encode(secret),
        "endpoint": base64.b64encode(endpoint),
    }


@mock.patch('kubernetes.config.load_kube_config')
@mock.patch('kubernetes.client.CoreV1Api')
class TestApi:

    """
    Tests for the API submodule.
    """

    def test_object(self, *_) -> None:
        """
        Verify the Auth object can be created regardless of Kubernetes' state,
        and that the token is not yet set.
        """
        auth = api.Auth()
        assert auth.token is None

    def test_secret(self, *_) -> None:
        """
        Verify that refreshing a secret results in setting the token correctly.
        """
        expected = 123
        auth = api.Auth()
        auth.core.read_namespaced_secret.return_value = MockV1Secret
        mock_response = io.StringIO(f'{{"access_token": {expected}}}')
        with mock.patch.object(request, 'urlopen', return_value=mock_response):
            auth.refresh_token()
            assert auth.token == expected

    def test_secret_exceptions(self, *_) -> None:
        """
        Verify our expected errors cause our custom error to be raised.
        """
        auth = api.Auth()
        auth.core.read_namespaced_secret.side_effect = client.exceptions.ApiException
        with pytest.raises(api.AuthException):
            auth.refresh_token()
        auth.core.read_namespaced_secret.side_effect = MaxRetryError(
            pool=None, url='foo'
        )
        with pytest.raises(api.AuthException):
            auth.refresh_token()
