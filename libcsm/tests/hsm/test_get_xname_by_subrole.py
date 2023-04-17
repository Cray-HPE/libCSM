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
from libcsm.hsm import get_xnames
import http
from requests import Session
import json


class MockHTTPResponse:
        def __init__(self, data, status_code):
            self.json_data = data
            self.status_code = status_code

        def json(self):
            return self.json_data


@mock.patch('kubernetes.config.load_kube_config')
@mock.patch('kubernetes.client.CoreV1Api')
class TestXnamesBySubrole:

    def test_get_xnames(self, *_) -> None:
        """
        Tests successful run of the HSM get_xnames_by_role_subrole function.
        """  
        print("Here in test")  
        hsm_role_subrole = "Management_Worker"
        
        status_code = http.HTTPStatus.OK
        data = { "Components": [
                    { "ID" : "1"},
                    { "ID" : "2"} 
                    ]
                }
        with mock.patch.object(Session, 'get', return_value=MockHTTPResponse(data, status_code)):
            xnames = get_xnames.get_xnames_by_role_subrole(None, hsm_role_subrole, Session)
            assert xnames == ['1','2']


    def test_get_xnames_bad_subrole(self, *_) -> None:
        """
        Tests run of the HSM get_xnames_by_role_subrole function with bad role_subrole.
        """    
        hsm_role_subrole = "Management_badSubrole"
        with pytest.raises(SystemExit):
            get_xnames.get_xnames_by_role_subrole(None, hsm_role_subrole, None)


    def test_get_xnames_bad_response(self, *_) -> None:
        """
        Tests run of the HSM get_xnames_by_role_subrole function with bad resonse from HMS.
        """    
        hsm_role_subrole = "Management_Master"
        status_code = http.HTTPStatus.UNAUTHORIZED
        data = { "Components": [
                    { "ID" : "1"},
                    { "ID" : "2"} 
                    ]
                }
        with mock.patch.object(Session, 'get', return_value=MockHTTPResponse(data, status_code)):
            with pytest.raises(SystemExit):
                get_xnames.get_xnames_by_role_subrole(None, hsm_role_subrole, Session)
    
