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
Tests for the hsm api submodule.
"""

import http
import pytest
import mock
from dataclasses import dataclass
from requests import Session

from libcsm import api
from libcsm.hsm import api as hsmApi


class MockHTTPResponse:
    def __init__(self, data, status_code):
        self.json_data = data
        self.status_code = status_code

    def json(self):
        return self.json_data


@dataclass()
class MockSetup:
    """
    Setup variables that are reused in tests
    """
    mock_components = [
        { "ID" : "1"},
        { "ID" : "2"},
    ]
    ok_mock_http_response=MockHTTPResponse(mock_components, http.HTTPStatus.OK)
    unauth_mock_http_response=MockHTTPResponse(mock_components, http.HTTPStatus.UNAUTHORIZED)

class TestHsmApi:

    hsm_api = None
    mock_setup = MockSetup

    @mock.patch('kubernetes.config.load_kube_config')
    @mock.patch('libcsm.api.Auth', spec=True)
    def setup_method(self, *_) -> None:
        """
        Setup HSM API to be used in tests
        """
        self.hsm_api = hsmApi.API()

    def test_get_components(self, *_) -> None:
        """
        Tests successful run of the HSM get_components function.
        """
        with mock.patch.object(Session, 'get', return_value=self.mock_setup.ok_mock_http_response):
            components = self.hsm_api.get_components('Management_Master')
            assert components == self.mock_setup.ok_mock_http_response

    def test_get_components_bad_subrole(self, *_) -> None:
        """
        Tests error is raised when bad role_subrole is provided.
        """
        with mock.patch.object(Session, 'get', return_value=self.mock_setup.ok_mock_http_response):
            with pytest.raises(KeyError):
                self.hsm_api.get_components('Management_bad_subrole')

    def test_get_components_bad_response(self, *_) -> None:
        """
        Tests error is raised when a bad response is recieved from session.get() function.
        """
        with mock.patch.object(Session, 'get', return_value=self.mock_setup.unauth_mock_http_response):
            with pytest.raises(Exception):
                self.hsm_api.get_components('Management_Worker')
