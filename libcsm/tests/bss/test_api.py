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

from dataclasses import dataclass
from requests import Session
from libcsm import api
from libcsm.bss import api as bssApi


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
    image_dict = {
        "initrd" : "initrd_image",
        "rootfs" : "rootfs_image",
        "kernel" : "kernel_image",
    }
    mock_boot_params = {
        "initrd" : "pre_initrd",
        "kernel" : "pre_kernel",
        "params" : "abc metal.server=pre_rootfs xyz",
    }


class TestBssApi:

    # setup variables that are reused in tests
    bss_api = None
    mock_setup = MockSetup

    @mock.patch('kubernetes.config.load_kube_config')
    @mock.patch('libcsm.api.Auth', spec=True)
    def setup_method(self, *_) -> None:
        """
        Setup BSS API to be used in tests
        """
        self.bss_api = bssApi.API()

    def test_get_bss_bootparameters(self, *_) -> None:
        """
        Tests successful run of the BSS get_bss_bootparameters function.
        """
        mock_bss_response = self.mock_setup.ok_mock_http_response
        with mock.patch.object(Session, 'get', return_value=mock_bss_response):
            boot_params = self.bss_api.get_bss_bootparams('some_xname')
            assert boot_params == self.mock_setup.mock_components[0]

    def test_get_bss_bootparameters_bad_response(self, *_) -> None:
        """
        Tests bad response from the BSS get_bss_bootparameters function.
        """
        mock_bss_response = self.mock_setup.unauth_mock_http_response
        with mock.patch.object(Session, 'get', return_value=mock_bss_response):
            with pytest.raises(Exception):
                self.bss_api.get_bss_bootparams('some_xname')


    def test_patch_bss_bootparameters(self, *_) -> None:
        """
        Tests successful run of the BSS get_patch_bootparameters function.
        """
        mock_bss_response = self.mock_setup.ok_mock_http_response
        with mock.patch.object(Session, 'patch', return_value=mock_bss_response):
            self.bss_api.patch_bss_bootparams('some_xname', [{'json_key': 'json_value'}])

    def test_patch_bss_bootparameters_bad_response(self, *_) -> None:
        """
        Tests bad response from the BSS patch_bss_bootparameters function.
        """
        mock_bss_response = self.mock_setup.unauth_mock_http_response
        with mock.patch.object(Session, 'get', return_value=mock_bss_response):
            with pytest.raises(Exception):
                self.bss_api.patch_bss_bootparams('some_xname', [{'json_key': 'json_value'}])

    def test_set_bss_image(self, *_) -> None:
        """
        Tests successful set_bss_image function.
        """
        with mock.patch.object(self.bss_api, 'get_bss_bootparams', return_value=self.mock_setup.mock_boot_params):
            with mock.patch.object(self.bss_api, 'patch_bss_bootparams', return_value=None):
                self.bss_api.set_bss_image("xname", self.mock_setup.image_dict)

    def test_set_bss_image_bad_inputs(self, *_) -> None:
        """
        Tests bad run of set_bss_image function because of invalid image_dict passed in.
        """
        image_dict = {
            "XX_bad_XX" : "initrd_image",
            "rootfs" : "rootfs_image",
            "kernel" : "kernel_image",
        }
        with pytest.raises(Exception):
            self.bss_api.set_bss_image("xname", image_dict)

    def test_set_bss_image_bad_boot_params1(self, *_) -> None:
        """
        Tests set_bss_image failure when bad boot params function.
        """
        bad_mock_boot_params = {
            "XX-bad" : "pre_initrd",
            "kernel" : "pre_kernel",
            "params" : "abc metal.server=pre_rootfs xyz",
        }
        with mock.patch.object(self.bss_api, 'get_bss_bootparams', return_value=bad_mock_boot_params):
            with pytest.raises(Exception):
                self.bss_api.set_bss_image("xname", self.mock_setup.image_dict)

    def test_set_bss_image_bad_boot_params2(self, *_):
        """
        Tests set_bss_image failure when bad boot params function.
        """
        bad_mock_boot_params = {
            "initrd" : "pre_initrd",
            "kernel" : "pre_kernel",
            "params" : "abc metal.sXXX=pre_rootfs xyz",
        }
        with mock.patch.object(self.bss_api, 'get_bss_bootparams', return_value=bad_mock_boot_params):
            with pytest.raises(Exception):
                self.bss_api.set_bss_image("xname", self.mock_setup.image_dict)