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
Tests for the hsm get_xnames_by_subrole submodule.
"""

import http
from dataclasses import dataclass
import pytest
import mock

from requests import Session
from libcsm import api
from libcsm.sls import api as slsApi


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
        {'Parent': 'par1', 'Xname': 'xname1',  'ExtraProperties': {'Aliases': ['ncn-w001'], 'A': 100}},
        {'Parent': 'par2', 'Xname': 'xname2',  'ExtraProperties': {'Aliases': ['ncn-s002'], 'A': 101}},
    ]
    ok_mock_http_response=MockHTTPResponse(mock_components, http.HTTPStatus.OK)
    unauth_mock_http_response=MockHTTPResponse(mock_components, http.HTTPStatus.UNAUTHORIZED)
    bad_mock_components = [
        {'Parent': 'par1', 'Xname': 'xname1',  'No_extra_properties': {'Aliases': ['ncn-w001'], 'A': 100}},
        {'Parent': 'par2', 'Xname': 'xname2',  'No_extra_properties': {'Aliases': ['ncn-s002'], 'A': 101}},
    ]
    bad_mock_http_response=MockHTTPResponse(bad_mock_components, http.HTTPStatus.OK)


class TestSLSApi:

    mock_setup = MockSetup
    sls_api = None

    @mock.patch('kubernetes.config.load_kube_config')
    @mock.patch('libcsm.api.Auth', spec=True)
    def setup_method(self, *_) -> None:
        """
        Setup SLS API to be used in tests
        """
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            self.sls_api = slsApi.API()

    def test_get_management_components_from_sls(self, *_) -> None:
        """
        Tests successful run of the SLS get_management_components_from_sls function.
        """
        with mock.patch.object(Session, 'get', return_value=self.mock_setup.ok_mock_http_response):
            self.sls_api.get_management_components_from_sls()

    def test_get_management_components_from_sls_error(self, *_) -> None:
        """
        Tests unsuccessful run of the SLS get_management_components_from_sls function because of bad response.
        """
        with mock.patch.object(Session, 'get', return_value=self.mock_setup.unauth_mock_http_response):
            with pytest.raises(Exception):
                self.sls_api.get_management_components_from_sls()

    def test_get_xname(self, *_) -> None:
        """
        Tests response from the SLS get_xname function.
        """
        with mock.patch.object(self.sls_api, 'get_management_components_from_sls', return_value=self.mock_setup.ok_mock_http_response):
            ret_xname = self.sls_api.get_xname('ncn-w001')
            assert ret_xname == 'xname1'

    def test_get_xname_bad_xname(self, *_) -> None:
        """
        Tests the SLS get_xname function fails given bad hostname.
        """
        with mock.patch.object(self.sls_api, 'get_management_components_from_sls', return_value=self.mock_setup.ok_mock_http_response):
            with pytest.raises(Exception):
                self.sls_api.get_xname('ncn-BAD')

    def test_get_xname_invalid_response(self, *_) -> None:
        """
        Tests the SLS get_xname function fails given bad component response.
        """
        with mock.patch.object(self.sls_api, 'get_management_components_from_sls', return_value=self.mock_setup.bad_mock_http_response):
            with pytest.raises(KeyError):
                self.sls_api.get_xname('ncn-w001')

    def test_get_hostname(self, *_) -> None:
        """
        Tests response from the SLS get_hostname function.
        """
        with mock.patch.object(self.sls_api, 'get_management_components_from_sls', return_value=self.mock_setup.ok_mock_http_response):
            ret_hostname = self.sls_api.get_hostname('xname1')
            assert ret_hostname == 'ncn-w001'

    def test_get_hostname_bad_xname(self, *_) -> None:
        """
        Tests the SLS get_hostname function fails given bad xname.
        """
        with mock.patch.object(self.sls_api, 'get_management_components_from_sls', return_value=self.mock_setup.ok_mock_http_response):
            with pytest.raises(Exception):
                self.sls_api.get_hostname('badXname')

    def test_get_hostname_invalid_response(self, *_) -> None:
        """
        Tests the SLS get_xname function with an invalid response from sls.get_management_components_from_sls.
        """
        with mock.patch.object(self.sls_api, 'get_management_components_from_sls', return_value=self.mock_setup.bad_mock_http_response):
            with pytest.raises(KeyError):
                self.sls_api.get_hostname('xname2')
