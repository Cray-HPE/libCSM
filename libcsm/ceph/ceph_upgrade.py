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
Submodule for starting and validating a Ceph upgrade.
"""
import subprocess
import json
import rbd
import rados
import sys
import re
from argparse import ArgumentParser
from prettytable import PrettyTable
from packaging import version
import time
import os
from libcsm.ceph import api
from libcsm.os import run_command

class ImagePullException(Exception):

    """
    An exception for a failure to pull image using podman.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class Upgrade:

    def __init__(self, upgrade_version: str, registry='registry.local') -> None:
        self.ceph_api = api.API()
        self.starting_version = ceph_api.get_ceph_version()
        self.upgrade_version = upgrade_version
        self._validate_version_format()
        self.registry = registry
        self._verify_valid_registry()
        self.registry_prefix = self._get_registry_prefix()

    def _validate_version_format(self) -> None:
        """
        Verifies a valid version was provided and that this version
        is higher than the current version.
        """
        is_valid = False
        matches = re.fullmatch('^v[0-9]+[.][0-9]+[.][0-9]+$', version)
        if matches != None:
            is_valid = True
            # remove first v from the upgrade_version
            self.upgrade_version = self.upgrade_version[1:]
            return
        matches = re.fullmatch('^[0-9]+[.][0-9]+[.][0-9]+$', version)
        if matches != None:
            is_valid = True
            return
        if not is_valid:
            raise ValueError(f'Error upgrade version: {self.upgrade_version} is not a valid format. \
                Valid formats are \'v.X.X.X\' and \'X.X.X\' where X is an integer.')

    def _verify_valid_registry(self) -> None:
        """
        Validates that the registry provided is a valid option.
        """
        valid_registries = ['registry.local', 'localhost', 'localhost:5000', 'artifactory.algol60.net']
        if self.registry not in  valid_registries:
            raise ValueError(f'{self.registry} is not a valid registry. Valid registries are \
                {valid_registries}.')

    def _get_registry_prefix(self) -> str:
        """
        Gets the prefix for the image location based on the registry.
        """
        if self.registry == 'registry.local' or self.registry == 'localhost:5000':
            return (self.registry + '/')
        if self.registry == 'artifactory.algol60.net':
            return ''
        if self.registry == 'localhost':
            return 'localhost:5000/'

    def _verify_upgrade_version(self) -> bool:
        """
        Checks that the version being run is a greater version than the Ceph version
        that is currently running.
        """
        if not version.parse(self.starting_version) < version.parse(self.upgrade_version):
            raise ValueError(f'Cannot upgrade Ceph. The upgrade version:{self.upgrade_version} \
            is not greater than the current Ceph version running:{self.starting_version}.')

    def _check_image_pull(self, image: str) -> bool:
        """
        Checks that an image can be pulled using podman pull.
        """
        result = run_command(['podman', 'pull', image])
        if result.return_code != 0:
            raise ImagePullException(f"Error: failed to pull image from podman. {result.stderr}")

    def initiate_upgrade(self, version: str) -> None:
        """
        Start Ceph upgrade. First it checks that it is able to pull the upgrade image and 
        the version is valid to upgrade to.
        """
        upgrade_image = self.registry_prefix + \
            'artifactory.algol60.net/csm-docker/stable/quay.io/ceph/ceph:v' + self.upgrade_version
        self._verify_upgrade_version()
        self._check_image_pull(upgrade_image)
        # start upgrade
        upgrade_cmd = {"prefix":"orch upgrade start", "image":upgrade_image}
        self.ceph_api.cluster.mon_command(json.dumps(upgrade_cmd), b'', timeout=5)
        self.ceph_api.cluster.disconnect()
