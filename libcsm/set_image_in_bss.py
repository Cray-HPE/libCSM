#! /usr/bin/env python3
#
# MIT License
#
# (C) Copyright 2021-2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
import argparse
import http
import sys
import requests
import json
import os
import urllib3
import boto3
import botocore
import subprocess
import sys
import io

from argparse import ArgumentParser
from subprocess import Popen, PIPE
from botocore.config import Config

urllib3.disable_warnings()

S3_CONNECT_TIMEOUT=60
S3_READ_TIMEOUT=1

def get_xnames_by_subrole(api_gateway_address, subrole, session):
    token = os.environ.get('TOKEN')

    components_response = session.get('https://{}/apis/smd/hsm/v2/State/Components?role=Management&subrole={}'.format(
        api_gateway_address, subrole),
        headers={'Authorization': 'Bearer {}'.format(token)})
    if components_response.status_code != http.HTTPStatus.OK:
        print('ERROR Failed to get components with subrole {}'.format(subrole))
    xnames = []
    if components_response is not None:
        for component in components_response.json()['Components']:
            xnames.append(component['ID'])
    else:
        print('ERROR no componenets were found with hsm_role_subrole: Management_{}'.format(subrole))
    return xnames

def verify_bucket_exists(bucket):
    p = Popen(['radosgw-admin', 'bucket', 'list', '--bucket', bucket], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    output, error = p.communicate()
    if p.returncode != 0:
        print("ERROR bucket %s not found." % bucket, file = sys.stderr)
        sys.exit(1)

def get_object_owner(bucket, object_name):
    p = Popen(['radosgw-admin', 'object', 'stat', '--object', object_name, '--bucket', bucket], encoding='ISO-8859-1', stdout=PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        print("ERROR failed to get the owner of object: {} in bucket: {}. Verify that {} exists.". format(object_name, bucket, object_name))
        sys.exit(1)
    info = json.loads(output)
    owner = info['policy']['owner']['id']
    return owner

def get_creds(owner):
    p = Popen(['radosgw-admin', 'user', 'info', '--uid', owner], universal_newlines=True, stdout=PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        sys.exit(1)
    info = json.loads(output)
    a_key = info['keys'][0]['access_key']
    s_key = info['keys'][0]['secret_key']
    return a_key, s_key

def get_image_info(bucket_name, image_id, endpoint_url):
    image_manifest = image_id + "/manifest.json"
    owner = get_object_owner(bucket_name, image_manifest)
    a_key, s_key = get_creds(owner)
    s3_config = Config(connect_timeout=S3_CONNECT_TIMEOUT,
                           read_timeout=S3_READ_TIMEOUT)
    s3_resource = boto3.resource('s3',
                        endpoint_url=endpoint_url,
                        aws_access_key_id=a_key,
                        aws_secret_access_key=s_key,
                        config=s3_config)

    s3_object = s3_resource.Object(bucket_name, image_manifest).get()
    image_dict = {}
    object_json = json.loads(s3_object['Body'].read())
    images_json = object_json['artifacts']
    for image_type in ["initrd", "kernel", "rootfs"]:
        for image in images_json:
            if image_type in image['type']:
                image_dict[image_type] = image['link']['path']
                break
        try:
            if image_dict[image_type] is None:
                print("ERROR could not find image for {}".format(image_type))
                sys.exit(1)
        except:
            print("ERROR could not find image for {}".format(image_type))
            sys.exit(1)

    print("Using images: ", image_dict)
    return image_dict

def main():
    # Check to make sure we have a token.
    token = os.environ.get('TOKEN')
    if token is None:
        print("TOKEN environment variable must be set!")
        sys.exit(1)

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
        if args.hsm_role_subrole not in ["Management_Master", "Management_Worker", "Management_Storage"]:
            print('ERROR hsm_role_subrole: {} is not valid. Valid hsm_role_subrole options are Management_Master, Management_Worker, or Management_Storage'.format(args.hsm_role_subrole))
            sys.exit(1)
        if "Management_Master" == args.hsm_role_subrole:
            components += get_xnames_by_subrole(args.api_gateway_address, "Master", session)
        elif "Management_Worker" == args.hsm_role_subrole:
            components += get_xnames_by_subrole(args.api_gateway_address, "Worker", session)
        elif "Management_Storage" == args.hsm_role_subrole:
            components += get_xnames_by_subrole(args.api_gateway_address, "Storage", session)

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
                                headers={'Authorization': 'Bearer {}'.format(token),
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
                            headers={'Authorization': 'Bearer {}'.format(token),
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
                                headers={'Authorization': 'Bearer {}'.format(token),
                                            "Content-Type": "application/json"},
                                data=json.dumps(body))
        bss_json = bss_response.json()[0]
        print("  Metal.server image: ", bss_json['params'].split("metal.server=", 1)[1].split(" ",1)[0])
        print("  Initrd image:       ", bss_json['initrd'])
        print("  Kernel image:       ", bss_json['kernel'])
