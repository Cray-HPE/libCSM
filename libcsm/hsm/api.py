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
Submodule for interacting with CSM HSM.
"""

import http
from os import getenv
import requests
import certifi
from libcsm import api

ROLE_SUBROLES = ["Management_Master", "Management_Worker", "Management_Storage"]

class API:
    """
    Class for providing API to interact with HSM.
    """

    def __init__(self, api_gateway_address="api-gw-service-nmn.local"):

        self.api_gateway_address = api_gateway_address
        self.hsm_components_url = f'https://{self.api_gateway_address}/apis/smd/hsm/v2/State/Components'
        self._auth = api.Auth()
        self._auth.refresh_token()
        self._crt_path = getenv("REQUESTS_CA_BUNDLE", certifi.where())


    def get_components(self, role_subrole: str):
        """
        Function to get management components from HSM based on their role and subrole.
        """
        # get session
        session = requests.Session()
        session.verify = self._crt_path
        # get components
        if role_subrole not in ROLE_SUBROLES:
            raise KeyError(f'ERROR {role_subrole} is not a valid role_subrole')
        subrole = role_subrole.split("_")[1]
        try:
            components_response = session.get(self.hsm_components_url + f'?role=Management&subrole={subrole}',
                headers={'Authorization': 'Bearer {}'.format(self._auth.token)})
        except requests.exceptions.RequestException as ex:
            print(f'ERROR exception: {type(ex).__name__} when trying to get components')
        if components_response.status_code != http.HTTPStatus.OK:
            raise Exception(f'ERROR Failed to get components with subrole {subrole}')
        
        return components_response
