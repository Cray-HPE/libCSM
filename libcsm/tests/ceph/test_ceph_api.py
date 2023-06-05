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
Tests for the ceph_api submodule.
"""

import rados
from libcsm.ceph import api


# class MockCephMonResponse:
#     """
#     A mock for ceph mon command response
#     """
#     def __init__() -> None:

#     id = b'foo-client'
#     secret = b'2fb9d9ad-3333-2222-1111-000000000000'
#     endpoint = b'https://example.com'
#     data = {
#         "client-id": base64.b64encode(id),
#         "client-secret": base64.b64encode(secret),
#         "endpoint": base64.b64encode(endpoint),
#     }


@mock.patch('rados.Rados')
@mock.patch('rados.Rados.connect')
class TestCephApi:
    """
    Testing the Ceph API submodule.
    """

    def test_ceph_api(self, *_) -> None:
        """
        Verify 
        """
        ceph_api = api.API()
        assert ceph_api.cluster is not None

    # def test_ceph_api_object_not_found(self, *_) -> None:
    #     """
    #     Verify init raises a rados.ObjectNotFound exception.
    #     """

