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

@mock.patch('kubernetes.config.load_kube_config')
class TestSLSApi:

    def test_get_management_components_from_sls(self, *_) -> None:
        """
        Tests successful run of the SLS get_management_components_from_sls function.
        """
        mock_components = [
                            { "ID" : "1"},
                            { "ID" : "2"}
                        ]
        mock_status = http.HTTPStatus.OK
        mock_sls_response = MockHTTPResponse(mock_components, mock_status)

        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            sls_api = slsApi.API()
            with mock.patch.object(Session, 'get', return_value=mock_sls_response):
                sls_api.get_management_components_from_sls()

    def test_get_management_components_from_sls_error(self, *_) -> None:
        """
        Tests unsuccessful run of the SLS get_management_components_from_sls function because of bad response.
        """
        mock_components = [
                            { "ID" : "1"},
                            { "ID" : "2"}
                        ]
        mock_status = http.HTTPStatus.UNAUTHORIZED
        mock_sls_response = MockHTTPResponse(mock_components, mock_status)

        with mock.patch.object(api.Auth, 'refresh_token', return_value=None): 
            sls_api = slsApi.API()
            with mock.patch.object(Session, 'get', return_value=mock_sls_response):
                with pytest.raises(Exception):
                    sls_api.get_management_components_from_sls()


    def test_get_xname(self, *_) -> None:
        """
        Tests response from the SLS get_xname function.
        """
        mock_components = [
                            {'Parent': 'par1', 'Xname': 'xname1',  'ExtraProperties': {'Aliases': ['ncn-w001'], 'A': 100}},
                            {'Parent': 'par2', 'Xname': 'xname2',  'ExtraProperties': {'Aliases': ['ncn-s002'], 'A': 101}}
                          ]
        mock_status = http.HTTPStatus.OK
        mock_sls_response = MockHTTPResponse(mock_components, mock_status)

        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            sls_api = slsApi.API()
            with mock.patch.object(sls_api, 'get_management_components_from_sls', return_value=mock_sls_response):
                ret_xname = sls_api.get_xname('ncn-w001')
                assert ret_xname == 'xname1'

    def test_get_xname_bad_xname(self, *_) -> None:
        """
        Tests the SLS get_xname function given bad hostname.
        """
        mock_components = [
                            {'Parent': 'par1', 'Xname': 'xname1',  'ExtraProperties': {'Aliases': ['ncn-w001'], 'A': 100}},
                            {'Parent': 'par2', 'Xname': 'xname2',  'ExtraProperties': {'Aliases': ['ncn-s002'], 'A': 101}}
                          ]
        mock_status = http.HTTPStatus.OK
        mock_sls_response = MockHTTPResponse(mock_components, mock_status)
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            sls_api = slsApi.API()
            with mock.patch.object(sls_api, 'get_management_components_from_sls', return_value=mock_sls_response):
                with pytest.raises(Exception):
                    sls_api.get_xname('ncn-BAD')

    def test_get_xname_invalid_response(self, *_) -> None:
        """
        Tests the SLS get_xname function given bad hostname.
        """
        mock_components = [
                            {'Parent': 'par1', 'Xname': 'xname1',  'No_extra_properties': {'Aliases': ['ncn-w001'], 'A': 100}},
                            {'Parent': 'par2', 'Xname': 'xname2',  'No_extra_properties': {'Aliases': ['ncn-s002'], 'A': 101}}
                          ]
        mock_status = http.HTTPStatus.OK
        mock_sls_response = MockHTTPResponse(mock_components, mock_status)
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            sls_api = slsApi.API()
            with mock.patch.object(sls_api, 'get_management_components_from_sls', return_value=mock_sls_response):
                with pytest.raises(KeyError):
                    sls_api.get_xname('ncn-w001')

    def test_get_hostname(self, *_) -> None:
        """
        Tests response from the SLS get_hostname function.
        """
        mock_components = [
                            {'Parent': 'par1', 'Xname': 'xname1',  'ExtraProperties': {'Aliases': ['ncn-w001'], 'A': 100}},
                            {'Parent': 'par2', 'Xname': 'xname2',  'ExtraProperties': {'Aliases': ['ncn-s002'], 'A': 101}}
                          ]
        mock_status = http.HTTPStatus.OK
        mock_sls_response = MockHTTPResponse(mock_components, mock_status)

        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            sls_api = slsApi.API()
            with mock.patch.object(sls_api, 'get_management_components_from_sls', return_value=mock_sls_response):
                ret_hostname = sls_api.get_hostname('xname1')
                assert ret_hostname == 'ncn-w001'

    def test_get_hostname_bad_xname(self, *_) -> None:
        """
        Tests the SLS get_hostname function given bad xname.
        """
        mock_components = [
                            {'Parent': 'par1', 'Xname': 'xname1',  'ExtraProperties': {'Aliases': ['ncn-w001'], 'A': 100}},
                            {'Parent': 'par2', 'Xname': 'xname2',  'ExtraProperties': {'Aliases': ['ncn-s002'], 'A': 101}}
                          ]
        mock_status = http.HTTPStatus.OK
        mock_sls_response = MockHTTPResponse(mock_components, mock_status)
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            sls_api = slsApi.API()
            with mock.patch.object(sls_api, 'get_management_components_from_sls', return_value=mock_sls_response):
                with pytest.raises(Exception):
                    sls_api.get_hostname('badXname')

    def test_get_hostname_invalid_response(self, *_) -> None:
        """
        Tests the SLS get_xname function with an invalid response from sls.get_management_components_from_sls.
        """
        mock_components = [
                            {'Parent': 'par1', 'Xname': 'xname1',  'No_extra_properties': {'Aliases': ['ncn-w001'], 'A': 100}},
                            {'Parent': 'par2', 'Xname': 'xname2',  'No_extra_properties': {'Aliases': ['ncn-s002'], 'A': 101}}
                          ]
        mock_status = http.HTTPStatus.OK
        mock_sls_response = MockHTTPResponse(mock_components, mock_status)
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            sls_api = slsApi.API()
            with mock.patch.object(sls_api, 'get_management_components_from_sls', return_value=mock_sls_response):
                with pytest.raises(KeyError):
                    sls_api.get_hostname('xname2')
