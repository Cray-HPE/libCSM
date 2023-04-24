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
Function to get xnames by subrole from HSM
"""
from libcsm import api
import sys
import json
import http
import requests

class API:
    def __init__(self, api_gateway_address="api-gw-service-nmn.local"):

        self.api_gateway_address = api_gateway_address
        self.bootparams_url = 'https://{}/apis/bss/boot/v1/bootparameters'.format(self.api_gateway_address)
        self.session = requests.Session()
        self.session.verify = False
        self._auth = api.Auth()
        self._auth.refresh_token()


    def get_bss_bootparams(self, xname: str):
        body = {'hosts': [xname]}
        try:
            bss_response = self.session.get(self.bootparams_url,
                                    headers={'Authorization': 'Bearer {}'.format(self._auth.token),
                                                "Content-Type": "application/json"},
                                    data=json.dumps(body))
        except requests.exceptions.RequestException as ex:
            print(f'ERROR exception: {type(ex).__name__} when trying to get bootparameters')
        if bss_response.status_code != http.HTTPStatus.OK:
            raise Exception('ERROR Failed to get BSS bootparameters for {}'.format(xname))
            return None
        return bss_response.json()[0]


    def patch_bss_bootparams(self, xname : str, bss_json):
        try:
            patch_response = self.session.patch(self.bootparams_url,
                                headers={'Authorization': 'Bearer {}'.format(self._auth.token),
                                        "Content-Type": "application/json"},
                                data=json.dumps(bss_json))
        except requests.exceptions.RequestException as ex:
            print(f'ERROR exception: {type(ex).__name__} when trying to patch bootparameters')
        if patch_response.status_code != http.HTTPStatus.OK:
            raise Exception('ERROR Failed to patch BSS bootparameters for {}'.format(component))
        else:
            print('BSS entry patched')