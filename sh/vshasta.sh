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
# Checks if a node is running on GCP er https://cloud.google.com/compute/docs/instances/detect-compute-engine
# Globals:
#   None
# Arguments:
#   None
# Output:
#   None
#   Returns 0 if "Google Compute Engine" is detected from dmidecode, 1 if not
#   Alternatively, when dmidecode is not available, returns 0 if "Metadata-Flavor: Google'" is detected from curling metadata.google.internal, 1 if not
#######################################
isgcp() {
  if command -v dmidecode > /dev/null 2>&1; then
    if dmidecode -s system-product-name | grep -q "Google Compute Engine"; then
      return 0
    else
      return 1
    fi
  # dmidecode is the preferred method, but not available on all platforms
  # so curl the metadata server as a fallback
  else
    if command -v curl > /dev/null 2>&1; then
      if curl -s metadata.google.internal -i | grep -q 'Metadata-Flavor: Google'; then
        return 0
      else
        return 1
      fi
    else
      # dmidecode and curl failed, so exit with error as we cannot determine if running on GCP
      echo >&2 "dmidecode and curl not found, cannot determine if running on GCP"
      return 1
    fi
  fi
}
