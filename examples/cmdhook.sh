#!/usr/bin/env sh
#-*-mode: Shell-script; coding: utf-8;-*-
_base=$(basename "$0")
_dir=$(cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P || exit 126)
export _base _dir

# Note: not using set -e or set -u for this example

#shellcheck disable=SC2034
SOURCEPREFIX="${_dir}/../sh/"
. "${_dir}/../sh/lib.sh"

trap libcleanup EXIT

wrapcmd curl jq ls rm

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
example post hook
command: $@
rc: $rc
stdin $stdin:
$(cat ${stdin})
stout $stdout:
$(cat ${stdout})
sterr $stderr:
$(cat ${stderr})
EOF
}

#shellcheck disable=SC2034
CURLPOSTHOOK=posthook
#shellcheck disable=SC2034
JQPOSTHOOK=posthook
#shellcheck disable=SC2034
RMPOSTHOOK=posthook
#shellcheck disable=SC2034
LSPOSTHOOK=posthook

curl uri://isinvalid | jq -r .
curl -s https://example.com/invalid | jq -r .

ls /does/not/exist
rm /does/not/exist
