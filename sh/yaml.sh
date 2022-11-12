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

# Function to convert a yaml bool string value(s) to a shell bool
# https://yaml.org/type/bool.html is all the valid values

# Validation function should be called before the bool function, otherwise the
# bool function will report false for invalid values.
yamlboolvalid() {
  case "${1?}" in
    y | Y | yes | Yes | YES | n | N | no | No | NO | 'true' | True | TRUE | 'false' | False | FALSE | on | On | ON | off | Off | OFF)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Expects valid inputs, if its invalid you get false the above function is on
# callers to use to ensure valid data is sent before calling.
yamlbool() {
  case "${1?}" in
    y | Y | yes | Yes | YES | 'true' | True | TRUE | on | On | ON)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}
