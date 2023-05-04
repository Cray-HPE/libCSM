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
Submodule for interacting with s3 objects.
"""
import sys
import json
import botocore
import boto3
import subprocess

from argparse import ArgumentParser
from subprocess import Popen, PIPE
from botocore.config import Config
from libcsm.os import run_command

S3_CONNECT_TIMEOUT=60
S3_READ_TIMEOUT=1

class S3Object:

    def __init__(self, bucket: str, object_name: str):
        self.bucket = bucket
        self.object_name = object_name
        self.owner = None
        self._a_key = None
        self._s_key = None
        self.verify_bucket_exists()

    def verify_bucket_exists(self) -> None:
        result = run_command(['radosgw-admin', 'bucket', 'list', '--bucket', self.bucket])
        if result.return_code != 0:
            raise Exception("{}".format(result.stderr))

    def get_object_owner(self) -> None:
        result = run_command(['radosgw-admin', 'object', 'stat', '--object', self.object_name, '--bucket', self.bucket])
        if result.return_code != 0:
            raise Exception("{}".format(result.stderr))
        info = json.loads(result.stdout)
        owner = info['policy']['owner']['id']
        self.owner = owner

    def get_creds(self) -> None:
        if self.owner is None:
            self.get_object_owner()
        result = run_command(['radosgw-admin', 'user', 'info', '--uid', self.owner])
        if result.return_code != 0:
            raise Exception("{}".format(result.stderr))
        info = json.loads(result.stdout)
        self._a_key = info['keys'][0]['access_key']
        self._s_key = info['keys'][0]['secret_key']

    def get_object(self, endpoint_url="http://rgw-vip"):
        if self.a_key is None or self.s_key is None:
            self.get_creds()
        s3_config = Config(connect_timeout=S3_CONNECT_TIMEOUT,
                            read_timeout=S3_READ_TIMEOUT)
        s3_resource = boto3.resource('s3',
                            endpoint_url=endpoint_url,
                            aws_access_key_id=self.a_key,
                            aws_secret_access_key=self.s_key,
                            config=s3_config)

        return s3_resource.Object(self.bucket, self.object_name).get()

    @property
    def a_key(self) -> str:
        """
        Get object access key.
        """
        return self._a_key
    
    @property
    def s_key(self) -> str:
        """
        Get object secret key.
        """
        return self._s_key