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

ROLES = ["Management"]
SUBROLES = ["Master", "Worker", "Storage"]
ROLE_SUBROLES = ["Management_Master", "Management_Worker", "Management_Storage"]

class API:
    def __init__(self, api_gateway_address="api-gw-service-nmn.local"):

        self.api_gateway_address = api_gateway_address
        self.bootparams_url = 'https://{}/apis/bss/boot/v1/bootparameters'.format(self.api_gateway_address)
        self.session = requests.Session()
        self.session.verify = False


    def get_bss_json(xname: str):
        # get token
        auth = api.Auth()
        auth.refresh_token()
        body = {'hosts': [xname]}
        bss_response = self.session.get(self.bootparams_url,
                                headers={'Authorization': 'Bearer {}'.format(auth.token),
                                            "Content-Type": "application/json"},
                                data=json.dumps(body))
        return bss_response.json()[0]


    def patch_bss_json(xname : str, bss_json):
        patch_response = self.session.patch(self.bootparams_url,
                            headers={'Authorization': 'Bearer {}'.format(auth.token),
                                    "Content-Type": "application/json"},
                            data=json.dumps(bss_json))
        if patch_response.status_code != http.HTTPStatus.OK:
            print('ERROR Failed to patch BSS entry for {}'.format(component))
            raise Error
        else:
            print('BSS entry patched')