#!/usr/bin/env bats
#
# MIT License
#
# (C) Copyright 2022 Hewlett Packard Enterprise Development LP
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
# source the script to be tested
source shell/csm-common.sh

# load the supplemental libraries
load 'bats-support/load'
load 'bats-assert/load'
load 'bats-file/load'

@test "test csm_version_from_tarball function" {
  local valid_remote_uri=https://example.com/path/to/csm-1.4.0-alpha.7.tar.gz
  local invalid_remote_uri=https://example.com/path/to/invalid.tar.gz
  local valid_local_path=/tmp/csm-1.3.0.tar.gz
  local invalid_local_path=invalid.tar.gz

  # test for a valid remote URI
  run csm-common::csm_version_from_tarball "${valid_remote_uri}"
  assert_success
  assert_output '1.4.0-alpha.7'
  # test for an invalid remote URI
  run csm-common::csm_version_from_tarball "${invalid_remote_uri}"
  assert_failure
  assert_output 'Expected local or remote path/to/csm-x.x.x.tar.gz, recieved: https://example.com/path/to/invalid.tar.gz'
  # test for a valid local path
  run csm-common::csm_version_from_tarball "${valid_local_path}"
  assert_success
  assert_output '1.3.0'
  # test for an invalid local path
  run csm-common::csm_version_from_tarball "${invalid_local_path}"
  assert_failure
  assert_output 'Expected local or remote path/to/csm-x.x.x.tar.gz, recieved: invalid.tar.gz'
  # test for providing no args
  run csm-common::csm_version_from_tarball
  assert_failure
  assert_output "Expected exactly 1 argument (URI or local path/to/csm-x.x.x.tar.gz), recieved 0"
    # test for providing too many args
  run csm-common::csm_version_from_tarball "foo" "bar"
  assert_failure 
  assert_output "Expected exactly 1 argument (URI or local path/to/csm-x.x.x.tar.gz), recieved 2"
}
