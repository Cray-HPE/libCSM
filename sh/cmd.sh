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

# This command is crazy, however its meant to help debug any executable
#
# There are current caveats as well. Those include:
# - This entirely *breaks* pipes, on purpose, so what was parallel execution
#   becomes serialized.
# - This also breaks output to not interleave stdout/stderr, stdout is output
#   then stderr, if this is an issue this may be improved but for now its non
#   negotiable.
# - This also writes out many files and basically invokes a bit of overhead per
#   call, this too is unavoidable, its a trampoline function that wraps the
#   command.
#
# Arguments to function are simply the non fully prefixed commands to wrap.
# Note, they *MUST* be on $PATH
#
# Of particular note is that if we are run under test, e.g. shellspec
# we prefix the command name with sut, e.g. wrapcmd foo will result in a
# trampoline function of sutfoo not foo. This is to enable shellspec
# itself to be able to unit test the trampoline setup function below.
#
# Future enhancements will set this up to write stuff out to a timeline
# directory of wrapped commands, return codes, stdin/out/err as files.
#
# That is a future me task.
wrapcmd() {
  # Bit of a cheat to ensure if we're run under set -u we can detect things.
  # We only do this if DEBUG is set to... whatever doesn't matter the value.
  # Nop if set and we return.
  if [ "" = "${DEBUG-}" ]; then
    return 0
  fi

  # Need to detect this outside of any wrapped command or hook or we detect the
  # pipes things might be ran in.
  _colors

  # You need to explicitly opt into system under test behavior (just changes the
  # function name in the end)
  SUT=${SUT:-false}

  for cmd in "$@"; do
    cmdname="${cmd}"
    # Not really applicable to ${cmdname} in this exec call
    #shellcheck disable=SC2086
    uppername="$(echo ${cmdname} | tr '[:lower:]' '[:upper:]')"
    evalcmd="${cmdname}"

    # Less copypasta is good...er
    UPRE="${uppername}PREHOOK"
    UPOST="${uppername}POSTHOOK"

    # If users want a default post hook set it up first the later evals will use
    # this if present. Note, don't setup this hook if there is already a hook.
    #
    # For the life of me I can't figure out how to do parameter expanstion
    # defaults in an eval here. Future me fix. TODO: Sorry its insane figure out
    # why ${blah:-${default}} no worky.

    # This is a huge hack future me red/green/refactor it.
    #shellcheck disable=SC2116 disable=SC2086
    eval "posthook=\$${UPOST}"
    defposthook="${DEFAULTPOSTHOOK}"

    # I had to do evil with the eval above...
    #shellcheck disable=SC2154
    if [ "${posthook}" != "" ]; then
      eval "${UPOST}=\$${UPOST}"
    elif [ "${defposthook}" != "" ]; then
      eval "${UPOST}=\${DEFAULTPOSTHOOK}"
    fi

    # TODO: pre/validate default hooks? Not sure that makes sense... Easy to add
    # if/when needed.
    if $SUT; then
      cmdname="sut${cmd}"
    else
      # Forgive me but I had to use eval for this atrocity, basically if wrapcmd
      # foo was called this defines FOO as a variable with the full path to
      # "foo". Aka FOO=/usr/bin/foo, this lets callers get at the underlying
      # command if needed directly. If in a rather wack way but it works, nobody
      # NEEDS to source this file unless they want the behavior.
      #
      # All this is in the end is this:
      # FOO=${FOO:-foo}
      # FOO=$(command -v ${FOO})
      #
      # But dynamic for any "foo". Don't focus on it too hard.

      # No shellcheck this should not be quoted
      #shellcheck disable=SC2086
      eval ${uppername}="\${${uppername}:-${cmdname}}"
      # Or this
      #shellcheck disable=SC2086
      eval export ${uppername}="\$(command -v \${$uppername})"
      evalcmd=\$${uppername}
    fi

    # Define all the default hook functions we might need, note that some
    # commands might need special defaults. That will be a different file. The
    # "defaults" will be to act just like the original command with no special hooks.
    #
    # The caveat here is simply that we do setup to use a default wrap hook
    # that does the following iff rc != 0 dumps out to stderr.
    # - Path of command and its arguments
    # - return code
    # - tempfile names used to store stdin/out/err
    # - and those file(s) content(s)
    #
    # Specific hook overrides like for say curl or jq are in another sh library
    # castle.

    # First hook definition and default env setup is a precondition hook.
    #
    # So with wrapcmd foo we get the following uneval'd shell:
    # FOOPREHOOK=${FOOPREHOOK-}
    # fooprehook() { [ -n "${FOOPREHOOK}" ] && "${FOOPREHOOK}" "$@" }
    #
    # Note this is before any stdin/stdout/stderr detection. All this hook gets
    # is args. This is *NOT* checked for return codes. Its meant as a way to say
    # set an env var that might be used in a later hook or even record the date
    # something ran. Whatever, just its here if needed/useful.
    #
    # Every one of these evals this is a non issue shellcheck.
    #shellcheck disable=SC2086
    eval "${UPRE}=\${${UPRE}-}"
    # # Don't stare too long into the \ abyss just accept the void...
    eval "
${cmd}prehook() {
  [ -n \"\$${UPRE}\" ] && \$${UPRE} \$@ || :;
}"

    # The second and final hook defined is basically the PREHOOK only called
    # right before return Here to do any cleanup you may want in the PREHOOK
    # really or record executation time whatever. You do you.
    #shellcheck disable=SC2086
    eval "${UPOST}=\${${UPOST}-}"
    # # Don't stare too long into the \ abyss just accept the void...
    eval "
${cmd}posthook() {
  [ -n \"\$${UPOST}\" ] && \$${UPOST} \$@ || :;
}"

    # I want to be clear, this entire things crazy enough as it is but this eval
    # is not for the faint of heart, here there definitely be dragons, hold onto
    # your butts.

    # Shellcheck gets super confused by this craziness, its FINE just ignore it.
    #shellcheck disable=SC2140
    eval "
${cmdname}() {
  ${cmd}prehook ${evalcmd} \"\$@\"

  if [ ! -t 0 ]; then
    stdin=\$(libtmpfile stdin-is-a-pipe)
    cat - /dev/stdin > \$stdin
  else
    # Its empty but eh
    stdin=\$(libtmpfile stdin)
  fi

  if ! [ -t 1 ]; then
    stdout=\$(libtmpfile stdout-is-a-pipe)
  else
    stdout=\$(libtmpfile stdout)
  fi

  if ! [ -t 2 ]; then
    stderr=\$(libtmpfile stderr-is-a-pipe)
  else
    stderr=\$(libtmpfile stderr)
  fi

  {
    # we need to be able to get at failed commands so for this once ensure we
    # aren't run under set -e, but just here.
    set +e
    if [ ! -z \$stdin ]; then
      ${evalcmd} "\$@" 2> \$stderr 1> \$stdout < \$stdin
    else
      ${evalcmd} "\$@" 2> \$stderr 1> \$stdout
    fi
  }
  rc=\$?

  # Cat out stdout first then stderr
  cat \$stdout >&1
  cat \$stderr >&2

  ${cmd}posthook \$rc \$stdin \$stdout \$stderr ${evalcmd} \"\$@\"
  return \$rc
}"
  done
}

# Dumb helper function for the post hook
_dump() {
  file="${1}"
  realfile=$(realpath "${file}")

  if [ -s "${realfile}" ]; then
    # Shellcheck can be annoying with quoting in a quoted $() call, its not
    # needed.
    #shellcheck disable=SC2086
    printf "%s:\n%s" "${realfile}" "$(cat ${realfile})"
  else
    printf "%s: file is empty no data present\n" "${realfile}"
  fi
}

_colors() {
  if [ -t 1 ] && [ "$(tput colors)" -ge 8 ]; then
    reset="$(tput sgr0)"
    red="$(tput setaf 1)"
    yellow="$(tput setaf 3)"
  fi
}

# Default post hook, aka where most of the "magic" happens
defaultposthook() {
  rc="${1}"
  shift
  stdin="${1}"
  shift
  stdout="${1}"
  shift
  stderr="${1}"
  shift

  if [ "${rc}" -gt 0 ]; then
    rcpre="${red}"
  fi

  if [ -s "${stderr}" ]; then
    stderrpre="${red}"
  fi

  #shellcheck disable=SC2086
  cat << EOF >&2
${yellow-}default cmdhook debug begin${reset-}

command: $@
${rcpre-}rc: $rc${reset-}
pwd: $(pwd)
stdin $(_dump ${stdin})
stdout $(_dump ${stdout})
stderr ${stderrpre-}$(_dump ${stderr})${reset-}

${yellow-}default cmdhook debug end${reset-}
EOF
}
