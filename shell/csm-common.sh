#!/usr/bin/env bash
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
#######################################
# Extract the canonical release version from a path to a tarball
# Globals:
#   None
# Arguments:
#   Local /path/to/tarball.tar.gz or https://remote.host/path/to/tarball.tar.gz
# Output:
#   Writes CSM version to stdout (example: csm-1.4.0-alpha.7.tar.gz)
#######################################
function csm-common::csm_version_from_tarball() {
  local path="${1}"
  local version

  # Return non-zero if arg quantity is incorrect
  if [[ $# -ne 1 ]]; then
    echo "Expected exactly 1 argument (URI or local path/to/csm-x.x.x.tar.gz), recieved $#"
    return 1
  fi

  # Validate inpuit: if the regex does not match a URI or local path to a tar.gz, fail
  if ! [[ "${path}" =~ ^(\w+:\/\/).*csm-.*\.tar\.gz$|csm-.*\.tar\.gz$ ]]; then
    echo "Expected local or remote path/to/csm-x.x.x.tar.gz, recieved: ${path}"
    return 1
  fi

  # Delete the longest matching pattern, '*/' from the start of $1, which will remove everything before the last slash, leaving just the filename
  path="${path##*/}"
  # Delete the pattern 'csm-' from the string
  path="${path/csm-/}"
  # Delete the pattern, '.tar.gz' from the trailing portion of $path, which removes the file extension
  version="${path%%.tar.gz}"

  echo "${version}"
  return 0
}
