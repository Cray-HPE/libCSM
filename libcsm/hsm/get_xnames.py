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

def get_xnames_by_role_subrole(api_gateway_address, hsm_role_subrole, session):
    auth = api.Auth()
    auth.refresh_token()
    # set default api gateway address
    if api_gateway_address == None:
        api_gateway_address = "api-gw-service-nmn.local"
    if hsm_role_subrole not in ["Management_Master", "Management_Worker", "Management_Storage"]:
        print('ERROR hsm_role_subrole: {} is not valid. Valid hsm_role_subrole options are Management_Master, Management_Worker, or Management_Storage'.format(hsm_role_subrole))
        sys.exit(1)
    subrole = hsm_role_subrole.split("_")[1]
    components_response = session.get('https://{}/apis/smd/hsm/v2/State/Components?role=Management&subrole={}'.format(
        api_gateway_address, subrole),
        headers={'Authorization': 'Bearer {}'.format(auth.token)})
    if components_response.status_code != http.HTTPStatus.OK:
        print('ERROR Failed to get components with subrole {}'.format(subrole))
        sys.exit(1)
    xnames = []
    if components_response is not None:
        for component in components_response.json()['Components']:
            xnames.append(component['ID'])
    else:
        print('ERROR no componenets were found with hsm_role_subrole: Management_{}'.format(subrole))
    return xnames