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
Function for setting boot-image in BSS.
"""

import sys
import click
import requests
from libcsm.sls import api


@click.command()
@click.option('--hostname', required=True, type=str, \
    help='hostname of the node whose Xname should be returned.')
@click.option('--api-gateway-address', required=False, type=str, default='api-gw-service-nmn.local',
    help='API gateway address. Default is \'api-gw-service-nmn.local\'.')
def main(hostname, api_gateway_address) -> None:
    """
    Get the Xname of a NCN given a hostname.
    This queries SLS for management nodes' information.
    """
    sls_api = api.API(api_gateway_address)
    try:
        print(sls_api.get_xname(hostname))
    except (requests.exceptions.RequestException, KeyError, ValueError) as error:
        print(f'{error}')
        sys.exit(1)
