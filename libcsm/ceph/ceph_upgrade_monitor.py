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


class CephUpgradeMonitor:

    def __init__(self, orig_version: str, upgr_version: str, conf_file='/etc/ceph/ceph.conf') -> None:
        self.ceph_api = api.API(conf_file)
        self.orig_version = orig_version
        self.upgr_version = upgr_version
        mon = {"prefix":"orch ps", "daemon_type":"mon", "format":"json"}
        mgr = {"prefix":"orch ps", "daemon_type":"mgr", "format":"json"}
        osd = {"prefix":"orch ps", "daemon_type":"osd", "format":"json"}
        mds = {"prefix":"orch ps", "daemon_type":"mds", "format":"json"}
        rgw = {"prefix":"orch ps", "daemon_type":"rgw", "format":"json"}
        crash = {"prefix":"orch ps", "daemon_type":"crash", "format":"json"}
        self.ceph_daemon_cmd = {"mon": mon, "mgr": mgr, "osd", osd, "rgw": rgw, "crash":crash}

    def get_upgrade_status_message(self) -> str:
        """
        Get the status of the ceph upgrade. Returns a json string.
        """
        upgrade_status_cmd = {"prefix":"orch upgrade status"}
        status = self.ceph_api.run_ceph_cmd(upgrade_status_cmd)
        return status[1]

    def print_upgrade_status(self) -> None:
        """
        Checks the current daemons running the old and new Ceph version.
        This prints a readable table of information.
        """
        table = PrettyTable(['Service', 'Total Original Version', 'Total Upgraded', 'Total Running'])
        for service, cmd in self.ceph_daemon_cmd.items():
            orig, upgraded, running = self.count_daemons_per_version(service)
            table.add_row([service, orig, upgraded, running])
        print(table)

    def count_daemons_per_version(self, service: str) -> (int, int, int):
        """
        Count how many daemons are running the original ceph version and how many
        are running the upgraded version
        """
        n_old, n_new, running = 0, 0, 0
        cmd = self.ceph_daemon_cmd[service]
        cmd_results = self.ceph_api.run_ceph_cmd(cmd)
        results = json.loads(cmd_results[1])
        for s in range(len(results)):
            status = (results[s]["status_desc"])
            if status == "running":
                running+=1
            version = (results[s]["version"])
            if version == orig_version:
                n_old+=1
            elif version == upgr_version:
                n_new+=1
            return (n_old, n_new, running)

    def check_upgrade_errors(self) -> str:
        """
        Checks if there are any errors during the Ceph upgrade.
        If there is an error it will return a string containing the error.
        If there are no errors, an empty string will be returned.
        """
        status_message = json.loads(self.get_upgrade_status_message())['message']
        if "error" in status_message.lower():
            time.sleep(10)
            status_message = json.loads(self.get_upgrade_status_message())['message']:
            if "error" in status_message.lower():
                return status_message
        return ""

    def check_upgrade_complete(self) -> bool:
        """
        Checks that the upgrade status shows no upgrade in progress.
        It will check 3 time in 10 seconds before returning because
        there are instances of the upgrade status being empty momentarily.
        """
        status = json.loads(self.get_upgrade_status_message())
        if status['in_progress']:
            return False
        # ceph upgrade status will have no target_image or services_completed if 
        # the upgrade has completed
        # check 3 times in 10 seconds to be sure it has completed
        for i in range(3):
            if status['target_image'] != None and services_complete != []:
                return False
            else:
                time.sleep(5)
                status = json.loads(self.get_upgrade_status_message())
        return True

    def check_all_daemons_upgraded(self) -> bool:
        """
        Check that all daemons are running the upgraded Ceph version.
        """
        success = True
        for service, cmd in self.ceph_daemon_cmd.items():
            orig, upgraded, running = self.count_daemons_per_version(service)
            if orig != 0:
                print(f'Error not all {service} daemons have been upgraded. \
                {orig} is still running the old version')
                success = False
            elif upgraded != running:
                # wait 1 minute to see if it starts
                time.sleep(60)
                orig, upgraded, running = self.count_daemons_per_version(service)
                if upgraded != running:
                    print(f'Error not all upgraded {service} daemons are running. /
                    {service} upgraded:{upgraded}, running:{running}')
                    success = False
        return success


    def monitor_upgrade(self) -> (bool, str):
        """
        Module to monitor the upgrade until it has completed or failed.
        This gets the upgrade status, checks for failures,
        and checks for upgrade completion.
        """
        while True:
            # print status
            self.print_upgrade_status()
            # check if there are errors
            error = self.check_upgrade_errors()
            if error != "":
                return (False, error)
            # check if the upgrade is completed
            if self.check_upgrade_complete():
                if self.check_all_daemons_upgraded():
                    return (True, "")
                else:
                    return (False, "Error: not all Ceph daemons were upgraded")
            time.sleep(45)
        self.ceph_api.disconnect()