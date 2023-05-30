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
Function to set the boot-image in BSS for a NCN node(s).
"""

import sys
import click

from libcsm.s3 import images
from libcsm.hsm import xnames as hsm_xnames
from libcsm.bss import api


@click.command()
@click.option('--hsm-role-subrole', required=False, type=str, default=None,
               help='HSM role and subrole of nodes to set BSS image (e.g. Management_Master, Management_Storage).')
@click.option('--xnames', required=False, type=str, default=None,
                help='Xnames of nodes to set BSS image of in comma separated list.')
@click.option('--image-id', type=str, required=True,
                help='image-id of image to set in BSS for specified nodes.')
@click.option('--bucket', required=False, type=str, default='boot-images',
               help='s3 bucket where the image is located. Defaults to "boot-images".')
@click.option('--api-gateway-address', required=False, type=str, default='api-gw-service-nmn.local',
               help='API gateway address. Default is \'api-gw-service-nmn.local\'.')
@click.option('--endpoint-url', required=False, type=str, default='http://rgw-vip',
               help='Address of the Rados-gateway endpoint.')
def main(hsm_role_subrole, xnames, image_id, bucket, api_gateway_address, endpoint_url) -> None:

    """Set the kernel, rootfs, and initrd images in BSS for specified node(s) given an image-id."""

    # check inputs
    if hsm_role_subrole is None and xnames is None:
        print("Input Error: --hsm-role-subrole or --xnames must be specified.")
        sys.exit(1)

    comp_xnames = []
    if hsm_role_subrole is not None:
        try:
            comp_xnames += hsm_xnames.get_by_role_subrole(hsm_role_subrole)
        except Exception as error:
            print(f'{error}')
            sys.exit(1)

    if xnames is not None:
        xnames_arr = xnames.split(",")
        for xname in xnames_arr:
            if xname not in comp_xnames:
                comp_xnames.append(xname)

    # get the image-id info
    try:
        image_dict = images.get_s3_image_info(bucket, image_id, endpoint_url)
    except Exception as error:
        print(f'ERROR was unable to get image info for {bucket} {image_id}. {error}')
        sys.exit(1)

    bss_api=api.API()
    print("Editing BSS data for components: ", comp_xnames)
    for component in comp_xnames:
        try:
            bss_api.set_bss_image(component, image_dict)
        except Exception as error:
            print(f'ERROR was unable to set image in bss for {component}. {error}')
            sys.exit(1)
