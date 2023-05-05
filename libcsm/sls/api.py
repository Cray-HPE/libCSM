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

import http
import requests
import json

from libcsm import api

class API:
    def __init__(self, api_gateway_address="api-gw-service-nmn.local"):

        self.api_gateway_address = api_gateway_address
        self.sls_url = 'https://{}/apis/sls/v1/'.format(self.api_gateway_address)
        self._auth = api.Auth()
        self._auth.refresh_token()

    def get_management_components_from_sls(self):
        # get session
        session = requests.Session()
        session.verify = False

        try:
            components_response = session.get(self.sls_url + 'search/hardware?extra_properties.Role=Management',
                headers={'Authorization': 'Bearer {}'.format(self._auth.token)})
        except requests.exceptions.RequestException as ex:
            print(f'ERROR exception: {type(ex).__name__} when trying to get components')
        if components_response.status_code != http.HTTPStatus.OK:
            raise Exception('ERROR Failed to get components with subrole {}'.format(subrole))

        return components_response

    def get_xname(self, hostname: str):

        components_response = self.get_management_components_from_sls()

        for node in components_response.json():
            try:
                if hostname in node['ExtraProperties']['Aliases']:
                    return node['Xname']
            except KeyError as error:
                raise KeyError('ERROR [ExtraProperties][Aliases] was not in the response from sls. \
                These fields are expected in the json response. The resonponse was {}'.format(components_response.json()))
        raise Exception(f'ERROR hostname:{hostname} was not found in management nodes.')