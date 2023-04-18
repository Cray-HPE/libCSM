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
Submodule for interacting with s3 objects or buckets.
"""
import sys
import json
import boto3
import botocore
import subprocess

from argparse import ArgumentParser
from subprocess import Popen, PIPE
from botocore.config import Config

S3_CONNECT_TIMEOUT=60
S3_READ_TIMEOUT=1

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