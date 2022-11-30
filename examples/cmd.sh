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
#-*-mode: Shell-script; coding: utf-8;-*-
_base=$(basename "$0")
_dir=$(cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P || exit 126)
export _base _dir

# Just an example of making this whole hook rigamarole optional if DEBUG is set
# or not.
if [ -n "${DEBUG}" ]; then
  #shellcheck disable=SC2034
  SOURCEPREFIX="${_dir}/../sh"
  #shellcheck source=./../sh/lib.sh
  . "${SOURCEPREFIX}/lib.sh"

  posthook() {
    rc="${1}"
    shift
    stdin="${1}"
    shift
    stdout="${1}"
    shift
    stderr="${1}"
    shift

    #shellcheck disable=SC2086
    cat << EOF >&2
example post hook begin

command: $@
rc: $rc
pwd: $(pwd)
stdin $stdin:
$(cat ${stdin})
stdout $stdout:
$(cat ${stdout})
stderr $stderr:
$(cat ${stderr})

example post hook end
EOF
  }

  #shellcheck disable=SC2034
  {
    CURLPOSTHOOK="${CURLPOSTHOOK:-posthook}"
    JQPOSTHOOK="${JQPOSTHOOK:-posthook}"
    RMPOSTHOOK="${RMPOSTHOOK:-posthook}"
    LSPOSTHOOK="${LSPOSTHOOK:-posthook}"
  }

  # We don't want word splitting here with this var.
  #shellcheck disable=SC2086
  wrapcmd ${WRAP:-curl jq ls rm}
fi

# Needs to be below the ${DEBUG} block as that would count as an unbound variable if it is not set
# Note: not using set -e or set -u for this example but here is where you want it.
# set -eu

# The "actual" script, note you could skip defining your own hook to save some
# lines but this is a complete example.
curl uri://isinvalid | jq -r .
jq -r . << EOF
this is not json
EOF

ls /does/not/exist
rm /does/not/exist
