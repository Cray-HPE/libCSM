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
Submodule for interacting with Ceph.
"""
import subprocess
import json
import rbd
import rados
import sys
from argparse import ArgumentParser
from prettytable import PrettyTable
from packaging import version
import time
import os


class API:
    
    def __init__(self, conf_file='/etc/ceph/ceph.conf') -> None:
        try:
            self.cluster = rados.Rados(conffile=conf_file)
        except rados.ObjectNotFound as ex:
            raise rados.ObjectNotFound(f'ERROR ceph.conf not found in /etc/ceph. {ex}') from ex
        self.cluster.connect(1)

    def disconnect(self) -> None:
        self.cluster.shutdown()

    def run_ceph_cmd(self, cmd: dict) -> None:
        """
        Executes a ceph command. Runs ceph mon_command function.
        """
        self.cluster.mon_command(json.dumps(cmd), b'', timeout=5)
    
    def get_ceph_version(self) -> str:
        """
        Get the version of Ceph currently running.
        """
        cmd = {"prefix":"version", "format":"json"}
        cmd_results = self.run_ceph_cmd(cmd)
        results = json.loads(cmd_results[1])
        for key,value in results.items():
            current_version = str(value.split(' ')[2])
        return current_version
