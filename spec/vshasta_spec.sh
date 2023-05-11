#!/usr/bin/env sh
# MIT License
#
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP
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
Describe "vshasta.sh"
  Include sh/vshasta.sh
    Context "isgcp when dmidecode exists and returns expected output"
    # mock that dmidecode exists
    command() {
      if [ "$1" = "-v" ] && [ "$2" = "dmidecode" ]; then
        echo "/usr/sbin/dmidecode"
        return 0
      fi
    }
    # mock expected dmidecode output
    dmidecode() {
      if [ "$1" = "-s" ] && [ "$2" = "system-product-name" ]; then
        echo "Google Compute Engine"
        return 0
      fi
    }

    It 'only returns true when on GCP'
      When call isgcp
      The status should be success
    End
  End
End

Describe "vshasta.sh"
  Include sh/vshasta.sh
    Context "isgcp when dmidecode exists and returns expected output"
    # mock that dmidecode exists
    command() {
      if [ "$1" = "-v" ] && [ "$2" = "dmidecode" ]; then
        echo "/usr/sbin/dmidecode"
        return 0
      fi
    }
    # mock unexpected dmidecode output
    dmidecode() {
      if [ "$1" = "-s" ] && [ "$2" = "system-product-name" ]; then
        echo "S2600WFT"
        return 0
      fi
    }

    It 'only returns false not on GCP'
      When call isgcp
      The status should be failure
    End
  End
End

Describe "vshasta.sh"
  Include sh/vshasta.sh
    Context "isgcp when dmidecode does not exist but curl does and returns expected output"
    # mock that dmidecode does not exist
    command() {
      if [ "$1" = "-v" ] && [ "$2" = "dmidecode" ]; then
        echo "sdsd"
        return 1
      fi
    }
    # mock expected curl output
    curl() {
      if [ "$1" = "-s" ] && [ "$2" = "metadata.google.internal" ]; then
        echo "HTTP/1.1 200 OK"
        echo "Metadata-Flavor: Google"
        echo "Content-Type: application/text"
        echo "Date: Tue, 18 Apr 2023 11:20:43 GMT"
        echo "Server: Metadata Server for VM"
        echo "Content-Length: 17"
        echo "X-XSS-Protection: 0"
        echo "X-Frame-Options: SAMEORIGIN"
        echo ""
        echo "computeMetadata/"
        return 0
      fi
    }

    It 'only returns true if on GCP'
      When call isgcp
      The status should be success
    End
  End
End

Describe "vshasta.sh"
  Include sh/vshasta.sh
    Context "isgcp when dmidecode and curl do not exist"
    # mock that dmidecode does not exist
    command() {
      if [ "$1" = "-v" ] && [ "$2" = "dmidecode" ]; then
        echo "sdsd"
        return 1
      fi
    }
    # mock expected curl output
    curl() {
      if [ "$1" = "-s" ] && [ "$2" = "metadata.google.internal" ]; then
        echo "HTTP/1.1 200 OK"
        echo "Metadata-Flavor: Google"
        echo "Content-Type: application/text"
        echo "Date: Tue, 18 Apr 2023 11:20:43 GMT"
        echo "Server: Metadata Server for VM"
        echo "Content-Length: 17"
        echo "X-XSS-Protection: 0"
        echo "X-Frame-Options: SAMEORIGIN"
        echo ""
        echo "computeMetadata/"
        return 0
      fi
    }

    It 'only returns true if on GCP'
      When call isgcp
      The status should be success
    End
  End
End
