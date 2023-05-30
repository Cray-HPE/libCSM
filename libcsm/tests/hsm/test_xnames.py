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

import pytest
import mock

from libcsm import api
from libcsm.hsm import api as hsmApi
from  libcsm.hsm import xnames

class MockHTTPResponse:
    def __init__(self, data, status_code):
        self.json_data = data
        self.status_code = status_code

    def json(self):
        return self.json_data

@mock.patch('libcsm.api.Auth', spec=True)
class TestXnames:

    def test_xnames(self, *_) -> None:
        """
        Tests successful run of the HSM get_xnames_by_role_subrole function.
        """
        hsm_role_subrole = "Management_Worker"
        mock_components = { 
            "Components": [
                { "ID" : "1"},
                { "ID" : "2"},
            ]
        }
        #mock_auth._token = "test_token_abc"
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with mock.patch.object(hsmApi.API, 'get_components', return_value=MockHTTPResponse(mock_components, 200)):
                xnames_arr = xnames.get_by_role_subrole(hsm_role_subrole)
                assert xnames_arr == ['1','2']


    def test_xnames_bad_subrole(self, *_) -> None:
        """
        Tests unsuccessful run of the HSM get_xnames_by_role_subrole function by providing a bad subrole.
        """
        hsm_role_subrole = "Management_bad_subrole"
        #mock_auth._token = "test_token_abc"
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with pytest.raises(KeyError):
                xnames.get_by_role_subrole(hsm_role_subrole)


    def test_xnames_with_no_components(self, *_) -> None:
        """
        Tests get run of HSM get_xnames_by_role_subrole where no components are returned
        """
        hsm_role_subrole = "Management_Storage"
        mock_components = { "Components": []
                        }
        #mock_auth._token = "test_token_abc"
        with mock.patch.object(api.Auth, 'refresh_token', return_value=None):
            with mock.patch.object(hsmApi.API, 'get_components', return_value=MockHTTPResponse(mock_components, 200)):
                xnames_arr = xnames.get_by_role_subrole(hsm_role_subrole)
                # check that xnames_arr is empty
                assert not xnames_arr
