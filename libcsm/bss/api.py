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
Submodule for interacting with CSM BSS.
"""

import json
import http
from os import getenv
import requests
import certifi
from libcsm import api


class API:

    """
    Class for providing API to interact with BSS.
    """

    def __init__(self, api_gateway_address="api-gw-service-nmn.local"):

        self.api_gateway_address = api_gateway_address
        self.bootparams_url = f'https://{self.api_gateway_address}/apis/bss/boot/v1/bootparameters'
        self._auth = api.Auth()
        self._auth.refresh_token()
        self._crt_path = getenv("REQUESTS_CA_BUNDLE", certifi.where())
        self.session = requests.Session()
        self.session.verify = self._crt_path


    def get_bss_bootparams(self, xname: str) -> str:
        """
        Get bootparameters from BSS for a specifed xname.
        """
        body = {'hosts': [xname]}
        try:
            bss_response = self.session.get(self.bootparams_url,
                                    headers={'Authorization': 'Bearer {}'.format(self._auth.token),
                                                "Content-Type": "application/json"},
                                    data=json.dumps(body))
        except requests.exceptions.RequestException as ex:
            print(f'ERROR exception: {type(ex).__name__} when trying to get bootparameters')
        if bss_response.status_code != http.HTTPStatus.OK:
            raise Exception(f'ERROR Failed to get BSS bootparameters for {xname}')
        return bss_response.json()[0]


    def patch_bss_bootparams(self, xname : str, bss_json) -> None:
        """
        Patch the bootparameters in BSS for a specified xname.
        """
        try:
            patch_response = self.session.patch(self.bootparams_url,
                                headers={'Authorization': 'Bearer {}'.format(self._auth.token),
                                        "Content-Type": "application/json"},
                                verify=self._crt_path,
                                data=json.dumps(bss_json))
        except requests.exceptions.RequestException as ex:
            print(f'ERROR exception: {type(ex).__name__} when trying to patch bootparameters')
        if patch_response.status_code != http.HTTPStatus.OK:
            raise Exception(f'ERROR Failed to patch BSS bootparameters for {xname}')
        print('BSS entry patched')

    def set_bss_image(self, xname: str, image_dict: dict) -> None:

        """
        Set the images in BSS for a specific xname.
        The inputs are the node's xname and a dictionary containing initrd, kernel, and roofs
        image paths that will be set in BSS.
        """

        if 'initrd' not in image_dict or 'kernel' not in image_dict or 'rootfs' not in image_dict:
            raise Exception(f"ERROR set_bss_image has inputs 'xname' and 'image_dictonary' where \
            'image_dictionary' is a dictionary containing values for 'initrd', 'kernel', and \
            'rootfs'. The inputs recieved were xname:{xname}, image_dictionary:{image_dict}")

        bss_json = self.get_bss_bootparams(xname)
        if 'initrd' not in bss_json or 'kernel' not in bss_json:
            raise Exception(f"BSS bootparams did not have the expected keys 'initrd' or 'kernel'. \
            Boot parameters recieved: {bss_json}")
        # set new images
        bss_json['initrd'] = image_dict['initrd']
        bss_json['kernel'] = image_dict['kernel']
        params = bss_json['params']
        try:
            current_rootfs = params.split("metal.server=", 1)[1].split(" ",1)[0]
        except Exception as exc:
            raise Exception(f"ERROR could not find current metal.server image in {xname} bss params") from exc

        bss_json['params'] = params.replace(current_rootfs, image_dict['rootfs'])

        self.patch_bss_bootparams(xname, bss_json)

        # verify images in BSS
        print(f"New images in BSS for {xname} are:")
        new_bss_json = self.get_bss_bootparams(xname)
        print("  Metal.server image: ", new_bss_json['params'].split("metal.server=", 1)[1].split(" ",1)[0])
        print("  Initrd image:       ", new_bss_json['initrd'])
        print("  Kernel image:       ", new_bss_json['kernel'])