#!/usr/bin/env bats
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
