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
import base64
import io

from dataclasses import dataclass
from urllib import request
import pytest

from kubernetes import client
from urllib3.exceptions import MaxRetryError
import mock
from libcsm import api
from libcsm.bss import bssApi
import http
from requests import Session
import json


class MockHTTPResponse:
    def __init__(self, data, status_code):
        self.json_data = data
        self.status_code = status_code

    def json(self):
        return self.json_data


class TestBssApi:

    @mock.patch('libcsm.api.Auth', spec=True)
    def test_get_bss_bootparameters(self, mock_auth):
        """
        Tests successful run of the BSS get_bss_bootparameters function.
        """  
        mock_auth._token = "test_token_abc"
        mock_components = [
                            { "ID" : "1"},
                            { "ID" : "2"} 
                          ]
        mock_status = http.HTTPStatus.OK
        mock_bss_response = MockHTTPResponse(mock_components, mock_status)
        bss_api = bssApi.API()
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with mock.patch.object(Session, 'get', return_value=mock_bss_response):
                boot_params = bss_api.get_bss_bootparams('some_xname')
                assert boot_params == mock_components[0]

    @mock.patch('libcsm.api.Auth', spec=True)
    def test_get_bss_bootparameters_bad_response(self, mock_auth):
        """
        Tests bad response from the BSS get_bss_bootparameters function.
        """  
        mock_auth._token = "test_token_abc"
        mock_components = [
                            { "ID" : "1"},
                            { "ID" : "2"} 
                          ]
        mock_status = http.HTTPStatus.UNAUTHORIZED
        mock_bss_response = MockHTTPResponse(mock_components, mock_status)
        bss_api = bssApi.API()
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with mock.patch.object(Session, 'get', return_value=mock_bss_response):
                with pytest.raises(Exception):
                    boot_params = bss_api.get_bss_bootparams('some_xname')


    @mock.patch('libcsm.api.Auth', spec=True)
    def test_patch_bss_bootparameters(self, mock_auth):
        """
        Tests successful run of the BSS get_patch_bootparameters function.
        """  
        mock_auth._token = "test_token_abc"
        mock_components = [
                            { "ID" : "1"},
                            { "ID" : "2"} 
                          ]
        mock_status = http.HTTPStatus.OK
        mock_bss_response = MockHTTPResponse(mock_components, mock_status)
        bss_api = bssApi.API()
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with mock.patch.object(Session, 'patch', return_value=mock_bss_response):
                boot_params = bss_api.patch_bss_bootparams('some_xname', [{'json_key': 'json_value'}])
                assert boot_params == None

    @mock.patch('libcsm.api.Auth', spec=True)
    def test_patch_bss_bootparameters_bad_response(self, mock_auth):
        """
        Tests bad response from the BSS patch_bss_bootparameters function.
        """  
        mock_auth._token = "test_token_abc"
        mock_components = [
                            { "ID" : "1"},
                            { "ID" : "2"} 
                          ]
        mock_status = http.HTTPStatus.UNAUTHORIZED
        mock_bss_response = MockHTTPResponse(mock_components, mock_status)
        bss_api = bssApi.API()
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with mock.patch.object(Session, 'get', return_value=mock_bss_response):
                with pytest.raises(Exception):
                    boot_params = bss_api.patch_bss_bootparams('some_xname', [{'json_key': 'json_value'}])
