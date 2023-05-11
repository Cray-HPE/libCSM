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
import json
import boto3

from botocore.config import Config
from libcsm.os import run_command

S3_CONNECT_TIMEOUT=60
S3_READ_TIMEOUT=1

class S3Object:

    """
    Class for getting s3 object infomation given a bucket and bject name.  
    """

    def __init__(self, bucket: str, object_name: str):
        self.bucket = bucket
        self.object_name = object_name
        self.owner = None
        self._a_key = None
        self._s_key = None
        self.verify_bucket_exists()

    def verify_bucket_exists(self) -> None:
        """
        Verify the bucket provided exists in s3.
        """
        result = run_command(['radosgw-admin', 'bucket', 'list', '--bucket', self.bucket])
        if result.return_code != 0:
            raise Exception(f"{result.stderr}")


    def get_object_owner(self) -> None:
        """
        Get the owner of an object.
        """
        result = run_command(['radosgw-admin', 'object', 'stat', '--object', self.object_name, '--bucket', self.bucket])
        if result.return_code != 0:
            raise Exception(f"{result.stderr}")
        info = json.loads(result.stdout)
        owner = info['policy']['owner']['id']
        self.owner = owner

    def get_creds(self) -> None:
        """
        Get the credentials to access the object based on the owner.
        """
        if self.owner is None:
            self.get_object_owner()
        result = run_command(['radosgw-admin', 'user', 'info', '--uid', self.owner])
        if result.return_code != 0:
            raise Exception(f"{result.stderr}")
        info = json.loads(result.stdout)
        self._a_key = info['keys'][0]['access_key']
        self._s_key = info['keys'][0]['secret_key']

    def get_object(self, endpoint_url="http://rgw-vip"):
        """
        Get the object from s3. Returns a bob3.resource.Object.
        """
        if self._a_key is None or self._s_key is None:
            self.get_creds()
        s3_config = Config(connect_timeout=S3_CONNECT_TIMEOUT,
                            read_timeout=S3_READ_TIMEOUT)
        s3_resource = boto3.resource('s3',
                            endpoint_url=endpoint_url,
                            aws_access_key_id=self._a_key,
                            aws_secret_access_key=self._s_key,
                            config=s3_config)

        return s3_resource.Object(self.bucket, self.object_name).get()

