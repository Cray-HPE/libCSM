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
import requests
from libcsm import api
from libcsm.requests.session import get_session


class API:
    """
    Class for providing API to interact with BSS.
    """

    def __init__(self, api_gateway_address="api-gw-service-nmn.local"):

        self.api_gateway_address = api_gateway_address
        self.bootparams_url = f'https://{self.api_gateway_address}/apis/bss/boot/v1/bootparameters'
        self._auth = api.Auth()
        self._auth.refresh_token()
        self.session = get_session()

    def get_bss_bootparams(self, xname: str) -> str:
        """
        Get bootparameters from BSS for a specifed xname.
        """
        body = {'hosts': [xname]}
        try:
            bss_response = self.session.get(self.bootparams_url,
                                    headers={'Authorization': f'Bearer {self._auth.token}',
                                                "Content-Type": "application/json"},
                                    data=json.dumps(body))
        except requests.exceptions.RequestException as ex:
            raise requests.exceptions.RequestException(f'ERROR exception:' \
                f'{type(ex).__name__} when trying to get bootparameters')
        if bss_response.status_code != http.HTTPStatus.OK:
            raise requests.exceptions.RequestException(f'ERROR Failed to get BSS' \
                f'bootparameters for {xname}. Recieved http response:' \
                f'{bss_response.status_code} from  BSS.')
        return bss_response.json()[0]

    def patch_bss_bootparams(self, xname : str, bss_json) -> None:
        """
        Patch the bootparameters in BSS for a specified xname.
        """
        try:
            patch_response = self.session.patch(self.bootparams_url,
                                headers={'Authorization': f'Bearer {self._auth.token}',
                                        "Content-Type": "application/json"},
                                data=json.dumps(bss_json))
        except requests.exceptions.RequestException as ex:
            raise requests.exceptions.RequestException(f'ERROR exception:' \
                f'{type(ex).__name__} when trying to patch bootparameters')
        if patch_response.status_code != http.HTTPStatus.OK:
            raise requests.exceptions.RequestException(f'ERROR Failed to patch BSS' \
                f'bootparameters for {xname}. Recieved {patch_response.status_code}' \
                f'from as BSS response.')
        print('BSS entry patched')

    def set_bss_image(self, xname: str, image_dict: dict) -> None:
        """
        Set the images in BSS for a specific xname.

        The inputs are the node's xname and a dictionary containing initrd, kernel, and roofs
        image paths that will be set in BSS.
        """
        if 'initrd' not in image_dict or 'kernel' not in image_dict or 'rootfs' not in image_dict:
            raise ValueError(f"ERROR set_bss_image has inputs 'xname' and 'image_dictonary' where" \
                f"'image_dictionary' is a dictionary containing values for 'initrd', 'kernel', " \
                f"and 'rootfs'. The inputs recieved were xname:{xname}, " \
                f"image_dictionary:{image_dict}")

        bss_json = self.get_bss_bootparams(xname)
        if 'initrd' not in bss_json or 'kernel' not in bss_json:
            raise KeyError(f"BSS bootparams did not have the expected keys 'initrd' or 'kernel'." \
                f"Boot parameters recieved: {bss_json}")
        # set new images
        bss_json['initrd'] = image_dict['initrd']
        bss_json['kernel'] = image_dict['kernel']
        params = bss_json['params']
        try:
            current_rootfs = params.split("metal.server=", 1)[1].split(" ",1)[0]
        except Exception as exc:
            raise KeyError(f"ERROR could not find current metal.server image in {xname}" \
                f"bss params") from exc

        bss_json['params'] = params.replace(current_rootfs, image_dict['rootfs'])

        self.patch_bss_bootparams(xname, bss_json)

        # verify images in BSS
        print(f"New images in BSS for {xname} are:")
        new_bss_json = self.get_bss_bootparams(xname)
        print("  Metal.server image: ", \
            new_bss_json['params'].split("metal.server=", 1)[1].split(" ",1)[0])
        print("  Initrd image:       ", new_bss_json['initrd'])
        print("  Kernel image:       ", new_bss_json['kernel'])
