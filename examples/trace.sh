#!/usr/bin/env sh
#-*-mode: Shell-script; coding: utf-8;-*-
_base=$(basename "$0")
_dir=$(cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P || exit 126)
export _base _dir

#shellcheck source=./../sh/lib.sh
#shellcheck disable=SC2086,SC2046
. ${SOURCEPREFIX:=$(dirname $(readlink -f "${_dir}/../sh/lib.sh"))}/lib.sh
tracing_enabled && enable_tracing "${_base}" jq ls curl grep ps

# warn() { printf "warning! $*\n" >&2; }
# info() { printf "information! $*\n" >&2; }
# debug() { printf "debug! $*\n" >&2; }

jq -r . << EOF
this is not json
EOF

ls /does/not/exist

# emerg "red alert!"
warn "This goes to the screen and to the trace file if enabled"
curl http://example.com/dne | jq -r . &
sleep 1 &
info "This only goes to the trace file by default"
debug "Debug also only goes to the trace file by default"

wait

debug "fin"
