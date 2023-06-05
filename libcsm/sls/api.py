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
Submodule for interacting with CSM SLS.
"""

import http
import requests
from libcsm import api
from libcsm.requests.session import get_session


class API:

    """
    Class for providing API to interact with SLS.
    """

    def __init__(self, api_gateway_address="api-gw-service-nmn.local"):

        self.api_gateway_address = api_gateway_address
        self.sls_url = f'https://{self.api_gateway_address}/apis/sls/v1/'
        self._auth = api.Auth()
        self._auth.refresh_token()

    def get_management_components_from_sls(self) -> requests.Response:
        """
        Function to retrieve all management components from SLS.
        """
        session = get_session()
        try:
            components_response = session.get(self.sls_url + \
                'search/hardware?extra_properties.Role=Management',
                headers={'Authorization': f'Bearer {self._auth.token}'})
        except requests.exceptions.RequestException as ex:
            raise requests.exceptions.RequestException(f'ERROR exception: {type(ex).__name__} \
                when trying to get management components from SLS') from ex
        if components_response.status_code != http.HTTPStatus.OK:
            raise requests.exceptions.RequestException(f'ERROR Bad response \
                recieved from SLS. Recived: {components_response}')

        return components_response

    def get_xname(self, hostname: str) -> str:
        """
        Function to get the xname of a node from SLS based on a provided hostname.
        """
        components_response = self.get_management_components_from_sls()

        for node in components_response.json():
            try:
                if hostname in node['ExtraProperties']['Aliases']:
                    return node['Xname']
            except KeyError as error:
                raise KeyError(f'ERROR [ExtraProperties][Aliases] was not in the \
                response from sls. These fields are expected in the json response. \
                The resonponse was {components_response.json()}') from error
        raise ValueError(f'ERROR hostname:{hostname} was not found in management nodes.')

    def get_hostname(self, xname: str) -> str:
        """
        Function to get the hostname of a management node from SLS based on a provided xname.
        """
        components_response = self.get_management_components_from_sls()

        for node in components_response.json():
            try:
                if xname == node['Xname']:
                    # assumes the hostname is the first entry in ['ExtraProperties']['Aliases']
                    return node['ExtraProperties']['Aliases'][0]
            except KeyError as error:
                raise KeyError(f'ERROR [ExtraProperties][Aliases] was not in the \
                    response from sls. These fields are expected in the json response. \
                    The resonponse was {components_response.json()}') from error
        raise ValueError(f'ERROR xname:{xname} was not found in management nodes.')
