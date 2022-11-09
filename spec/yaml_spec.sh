#!/usr/bin/env sh
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
_base=$(basename "$0")
_dir=$(cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P || exit 126)
export _base _dir

Describe 'yaml.sh'
  Include sh/yaml.sh

  Context 'booleans'
    # all true/falses https://yaml.org/type/bool.html
    Parameters
# y | Y | yes | Yes | YES | n | N | no | No | NO | 'true' | True | TRUE | 'false' | False | FALSE | on | On | ON | off | Off | OFF)
      # trues
      "#1" y
      "#2" Y
      "#3" yes
      "#4" Yes
      "#5" YES
      "#6" n
      "#7" N
      "#8" no
      "#9" No
      "#10" NO
      "#11" true
      "#12" True
      "#13" TRUE
      "#14" false
      "#15" False
      "#16" FALSE
      "#17" on
      "#18" On
      "#19" ON
      "#20" off
      "#21" Off
      "#22" OFF
    End

    It 'detects valid booleans'
      When call yamlboolvalid "$2"
      The status should equal 0
    End
  End

  Context 'truthinesseses'
    Parameters
      "#1" y
      "#2" Y
      "#3" yes
      "#4" Yes
      "#5" YES
      "#6" true
      "#7" True
      "#8" TRUE
      "#9" on
      "#10" On
      "#11" ON
    End

    It 'considers trues truthy'
      When call yamlbool "$2"
      The status should equal 0
    End
  End

  Context 'falsieness'
    Parameters
      "#1" n
      "#2" N
      "#3" no
      "#4" No
      "#5" NO
      "#6" false
      "#7" False
      "#8" FALSE
      "#9" off
      "#10" Off
      "#11" OFF
    End

    It 'detects valid booleans'
      When call yamlbool "$2"
      The status should equal 1
    End
  End

  Context 'garbage inputs that arent boolean-y'
    Parameters
      "#1" f
      "#2" F
      "#3" aldkfjdkf
      "#4" 34348u7v
      "#5" %
    End

    It 'detects invalid boolean values'
      When call yamlboolvalid "$2"
      The status should equal 1
    End
  End
End
