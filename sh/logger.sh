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

#
# Common logging library for posix shells.
#
# Follow RFC 5424/syslog for log levels/behavior.
#
# Ref: https://datatracker.ietf.org/doc/html/rfc5424
#
# Numerical  Severity             Meaning
#   Code
#
#    0       Emergency          : system is unusable
#    1       Alert              : action must be taken immediately
#    2       Critical           : critical conditions
#    3       Error              : error conditions
#    4       Warning            : warning conditions
#    5       Notice             : normal but significant condition
#    6       Informational      : informational messages
#    7       Debug              : debug-level messages

# LVL     0     1     2    3     4    5      6    7
SEVERITY="EMERG:ALERT:CRIT:ERROR:WARN:NOTICE:INFO:DEBUG"

# Default log level is info unless someone chooses a higher/lower level
# LOG_LEVEL=${LOG_LEVEL:-info}
LOG_LEVEL=${LOG_LEVEL:-warn}

# Basically get the index for the SEVERITY value, nothing special
# TODO: The log severity won't change at runtime, turn this all into simple eval
# statements that call static functions and save cpu O(n) time
sevtolvl() {
  lvl=$1
  if ! command -v _memo_sevtolvl_"${lvl}" > /dev/null 2>&1; then
    sev=$(echo "${lvl}" | tr '[:lower:]' '[:upper:]')
    idx=0
    for s in $(echo $SEVERITY | tr ':' ' '); do
      if [ "${sev}" = "${s}" ]; then
        break
      fi
      idx=$((idx + 1))
    done

    # The "memoize" logic here is simply define a function that returns the
    # value. Unless we need to ever change logging levels dynamically at/during
    # a script being run this is fine...
    eval "_memo_sevtolvl_${lvl}() { return ${idx}; }"
  fi

  _memo_sevtolvl_"${lvl}"
}

# Print out ^^^
log_state() {
  # No amount of quoting will nuke this non complaint on sevtolvl
  #shellcheck disable=SC2046
  printf "LOG_LEVEL=%s\nLOG_LEVEL_IDX=%s\n" "${LOG_SEV}" $(sevtolvl "${LOG_LEVEL}")
}

# General logging function
#
# Example calls:
# log ERROR message with whatever
# log error message with whatever
# error message with whatever
log() {
  _log_level=$1
  shift

  _log_sev=$(echo "${_log_level}" | tr '[:lower:]' '[:upper:]')
  _log_lc=$(echo "${_log_level}" | tr '[:upper:]' '[:lower:]')

  sevtolvl "${_log_sev}"
  _log_lhs=$?
  sevtolvl "${LOG_LEVEL}"
  _log_rhs=$?
  if [ $_log_lhs -le $_log_rhs ]; then
    # Note: do not switch $* to $@ here, in spaces/args with printf lie dragons.
    # (it split lines probably off IFS dunno for now, future me problem)
    #
    # For now dump to stderr no control over what goes to stdout, use printf for that?
    printf "%s: %s\n" "${_log_lc}" "$*" >&2
  fi

  if [ -n "${TRACEPREFIX}" ]; then
    cat << EOF >> "${TRACEPREFIX}/timeline"
${_log_lc}: $*
EOF
  fi
}

# Helper functions for typing less log ... statements
for lvl in emerg alert crit error warn notice info debug; do
  eval "
_LOG_LEVEL_${lvl}=$(sevtolvl)
${lvl}() {
  log ${lvl} \"\$@\"
}

_${lvl}() {
  LOG_LEVEL=${lvl} log ${lvl} \"\$@\"
}
"
done
