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
Reusable mocks for SLS requests.
"""
from dataclasses import dataclass
import http
from libcsm.tests.mock_objects.mock_http import MockHTTPResponse

@dataclass()
class MockSLSResponse:
    """
    Setup testing variables that are reused in tests
    """
    mock_components = [
        {
            'Parent': 'par1', 'Xname': 'xname1',
            'ExtraProperties': {'Aliases': ['ncn-w001'], 'A': 100}
        }, {
            'Parent': 'par2', 'Xname': 'xname2',
            'ExtraProperties': {'Aliases': ['ncn-s002'], 'A': 101}
        },
    ]
    mock_http_response = MockHTTPResponse(mock_components, http.HTTPStatus.OK)
    unauth_mock_http_response=MockHTTPResponse(mock_components, http.HTTPStatus.UNAUTHORIZED)
    bad_mock_components = [
        {
            'Parent': 'par1', 'Xname': 'xname1',
            'No_extra_properties': {'Aliases': ['ncn-w001'], 'A': 100}
        }, {
            'Parent': 'par2', 'Xname': 'xname2',  
            'No_extra_properties': {'Aliases': ['ncn-s002'], 'A': 101}
        },
    ]
    bad_mock_http_response=MockHTTPResponse(bad_mock_components, http.HTTPStatus.OK)
