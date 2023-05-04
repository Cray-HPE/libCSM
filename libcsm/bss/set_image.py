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
from libcsm.s3 import images
from libcsm.hsm import xnames
from libcsm.bss import api
import sys 
import json
import requests

from argparse import ArgumentParser


def main():

    # parse arguments
    parser = ArgumentParser(description='Set BSS image utility.')
    parser.add_argument('--hsm_role_subrole', action='store',
                        help='HSM role and subrole of nodes to set BSS image (e.g. Management_Master, Management_Storage).')
    parser.add_argument('--xnames', action='store',
                        help='Xnames of nodes to set BSS image of in comma separated list.')
    parser.add_argument('--image_id', action='store',
                        required=True, help='image_id of image to set in BSS for specified nodes.')
    parser.add_argument('--bucket', action='store', default='boot-images',
                        help='s3 bucket where the image is located.')
    parser.add_argument('--api_gateway_address', action='store', default='api-gw-service-nmn.local',
                        help='Address of the API gateway.')
    parser.add_argument('--endpoint_url', action='store', default='http://rgw-vip',
                        help='Address of the Rados-gateway endpoint.')
    args = parser.parse_args()

    # check inputs
    if args.hsm_role_subrole is None and args.xnames is None:
        print("Input Error: --hsm_role_subrole or --xnames must be specified.")
        sys.exit(1)

    comp_xnames = []
    if args.hsm_role_subrole is not None:
        try:
            comp_xnames += xnames.get_by_role_subrole(args.hsm_role_subrole)
        except Exception as error:
            print(f'{error}')
            sys.exit(1)

    if args.xnames is not None:
        xnames_arr = args.xnames.split(",")
        for xname in xnames_arr:
            if xname not in comp_xnames:
                comp_xnames.append(xname)

    # get the image-id info
    try:
        image_dict = images.get_s3_image_info(args.bucket, args.image_id, args.endpoint_url)
    except Exception as error:
        print('ERROR was unable to get image info for {} {}. {}'.format(args.bucket, args.image_id, error))
        sys.exit(1)

    bss_api=api.API()
    print("Editing BSS data for components: ", comp_xnames)
    for component in comp_xnames:
        try:
            bss_api.set_bss_image(component, image_dict)
        except Exception as error:
            print('ERROR was unable to set image in bss for {}. {}'.format(component, error))
            sys.exit(1)
