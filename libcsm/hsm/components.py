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
Submodule for interacting with components from HSM.
"""

import http
import requests
from libcsm import api
from libcsm.requests.session import get_session

ROLE_SUBROLES = ["Management_Master", "Management_Worker", "Management_Storage"]

def get_components(role_subrole: str, api_gateway_address="api-gw-service-nmn.local") \
    -> requests.Response:
    """
    Function to get management components from HSM based on their role and subrole.
    """
    auth = api.Auth()
    auth.refresh_token()
    session = get_session()
    hsm_components_url = f'https://{api_gateway_address}/\
apis/smd/hsm/v2/State/Components'
    # get components
    if role_subrole not in ROLE_SUBROLES:
        raise KeyError(f'ERROR {role_subrole} is not a valid role_subrole')
    subrole = role_subrole.split("_")[1]
    try:
        components_response = session.get(hsm_components_url + \
            f'?role=Management&subrole={subrole}',
            headers={'Authorization': f'Bearer {auth.token}'})
    except requests.exceptions.RequestException as ex:
        raise requests.exceptions.RequestException(f'ERROR exception: \
{type(ex).__name__} when trying to get components')
    if components_response.status_code != http.HTTPStatus.OK:
        raise requests.exceptions.RequestException(f'ERROR Failed \
to get components with subrole {subrole}')
    return components_response
