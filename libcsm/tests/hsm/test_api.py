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

import pytest
import mock
import http
from requests import Session
from kubernetes import client

from libcsm import api
from libcsm.hsm import api as hsmApi


class MockHTTPResponse:
    def __init__(self, data, status_code):
        self.json_data = data
        self.status_code = status_code

    def json(self):
        return self.json_data


class TestHsmApi:

    @mock.patch('libcsm.api.Auth', spec=True)
    def test_get_components(self, mock_auth):
        """
        Tests successful run of the HSM get_components function.
        """ 
        mock_auth._token = "test_token_abc"
        mock_components = { "Components": [
                            { "ID" : "1"},
                            { "ID" : "2"}
                            ]
                        }
        mock_status = http.HTTPStatus.OK
        mock_response = MockHTTPResponse(mock_components, mock_status)
        hsm_api = hsmApi.API()
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with mock.patch.object(Session, 'get', return_value=mock_response):
                components = hsm_api.get_components('Management_Master')
                assert components == mock_response

    @mock.patch('libcsm.api.Auth', spec=True)
    def test_get_components_bad_subrole(self, mock_auth):
        """
        Tests error is raised when bad role_subrole is provided.
        """  
        mock_auth._token = "test_token_abc"
        mock_components = { "Components": [
                            { "ID" : "1"},
                            { "ID" : "2"} 
                            ]
                        } 
        mock_status = http.HTTPStatus.OK
        mock_response = MockHTTPResponse(mock_components, mock_status)
        hsm_api = hsmApi.API()
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with mock.patch.object(Session, 'get', return_value=mock_response):
                with pytest.raises(KeyError):
                    hsm_api.get_components('Management_bad_subrole')


    @mock.patch('libcsm.api.Auth', spec=True)
    def test_get_components_bad_response(self, mock_auth):
        """
        Tests error is raised when a bad response is recieved from session.get() function.
        """  
        mock_auth._token = "test_token_abc"
        mock_components = { "Components": [
                            { "ID" : "1"},
                            { "ID" : "2"} 
                            ]
                        } 
        mock_status = http.HTTPStatus.UNAUTHORIZED
        mock_response = MockHTTPResponse(mock_components, mock_status)
        hsm_api = hsmApi.API()
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with mock.patch.object(Session, 'get', return_value=mock_response):
                with pytest.raises(Exception):
                    hsm_api.get_components('Management_Worker')
