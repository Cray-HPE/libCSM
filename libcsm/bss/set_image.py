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
Function for setting boot-image in BSS
"""
from libcsm import api
from s3_object import *
from libcsm import get_xnames_by_role_subrole
import sys 
import json
import requests

from argparse import ArgumentParser

def main():
    auth = api.Auth()
    auth.refresh_token()

    # parse arguments
    parser = argparse.ArgumentParser(description='Set BSS image utility.')
    parser.add_argument('--hsm_role_subrole', action='store',
                        help='HSM role and subrole of nodes to set BSS image (e.g. Management_Master, Management_Storage).')
    parser.add_argument('--xnames', action='store',
                        help='Xnames of nodes to set BSS image of in comma separated list.')
    parser.add_argument('--image_id', action='store',
                        required=True, help='image_id of image to set in BSS for specified nodes.')
    parser.add_argument('--api_gateway_address', action='store', default='api-gw-service-nmn.local',
                        help='Address of the API gateway.')
    parser.add_argument('--endpoint_url', action='store', default='http://rgw-vip',
                        help='Address of the Rados-gateway endpoint.')
    args = parser.parse_args()

    if args.hsm_role_subrole is None and args.xnames is None:
        print("Input Error: --hsm_role_subrole or --xnames must be specified.")
        sys.exit(1)

    session = requests.Session()
    session.verify = False

    components = []
    if args.hsm_role_subrole is not None:
        components += get_xnames_by_subrole(args.api_gateway_address, args.hsm_role_subrole, session)

    if args.xnames is not None:
        xnames = args.xnames.split(",")
        for xname in xnames:
            if xname not in components:
                components.append(xname)

    print("Editing BSS data for components: ", components)

    # verify we can access the boot-images bucket
    bucket_name="boot-images"
    verify_bucket_exists(bucket_name)

    # get the image-id info
    image_dict = get_image_info(bucket_name, args.image_id, args.endpoint_url)

    for component in components:
        body = {'hosts': [component]}
        bss_response = session.get('https://{}/apis/bss/boot/v1/bootparameters'.format(args.api_gateway_address),
                                headers={'Authorization': 'Bearer {}'.format(auth.token),
                                            "Content-Type": "application/json"},
                                data=json.dumps(body))
        bss_json = bss_response.json()[0]

        params = bss_json['params']
        # set new images
        bss_json['initrd'] = image_dict['initrd']
        bss_json['kernel'] = image_dict['kernel']
        try:
            current_rootfs = params.split("metal.server=", 1)[1].split(" ",1)[0]
        except:
            print("ERROR could not find current metal.server image in {} bss params".format(component))
            sys.exit(1)
        bss_json['params'] = params.replace(current_rootfs, image_dict['rootfs'])

        patch_response = session.patch('https://{}/apis/bss/boot/v1/bootparameters'.format(args.api_gateway_address),
                            headers={'Authorization': 'Bearer {}'.format(auth.token),
                                    "Content-Type": "application/json"},
                            data=json.dumps(bss_json))
        if patch_response.status_code != http.HTTPStatus.OK:
            print('ERROR Failed to patch BSS entry for {}'.format(component))
            sys.exit(1)
        else:
            print('BSS entry for {} patched.'.format(component))

        # verify images in BSS
        print("New images in BSS for {} are:".format(component))
        body = {'hosts': [component]}
        bss_response = session.get('https://{}/apis/bss/boot/v1/bootparameters'.format(args.api_gateway_address),
                                headers={'Authorization': 'Bearer {}'.format(auth.token),
                                            "Content-Type": "application/json"},
                                data=json.dumps(body))
        bss_json = bss_response.json()[0]
        print("  Metal.server image: ", bss_json['params'].split("metal.server=", 1)[1].split(" ",1)[0])
        print("  Initrd image:       ", bss_json['initrd'])
        print("  Kernel image:       ", bss_json['kernel'])