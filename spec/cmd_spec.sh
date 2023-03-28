#!/usr/bin/env sh
#shellcheck disable=SC2317
#
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
_base=$(basename "$0")
_dir=$(cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P || exit 126)
export _base _dir

export SOURCEPREFIX="${_base}"

# This is only used for testing the wrapper. A user should never set this to
# designate system under test.
export SUT=true

Describe 'cmd.sh'
  Include sh/internal.sh
  Include sh/cmd.sh

  # Here to do initial testing of if the function behaves Since ls probably
  #exists everywhere just picking on it, we won't test with it just using it as
  #a canary for the wrap function itself.
  Context 'wrapcmd ls works without DEBUG set'
    It 'wraps ls'
      When call wrapcmd ls
      The status should equal 0
    End
  End

  Context 'wrapcmd ls works with DEBUG set'
    Before 'wrapsetup'
    After 'wrapteardown'

    wrapsetup() {
      export DEBUG=sure
    }

    wrapteardown() {
      unset DEBUG
    }

    It 'wraps ls'
      When call wrapcmd ls
      The status should equal 0
    End
  End

  Context 'wrapcmd behaves in rc 0 case'
    # The "command"
    foo() {
      printf "stdout\n"
      printf "stderr\n" >&2
      return 0
    }

    Before 'wrapsetup'
    After 'wrapteardown'

    wrapsetup() {
      DEBUG=whynot wrapcmd foo
    }

    wrapteardown() {
      unset DEBUG
    }

    It 'wraps foo "command"'
      When call sutfoo
      The status should equal 0
      The stdout should equal "stdout"
      The stderr should equal "stderr"
    End
  End

  Context 'wrapcmd honors pre hook in 0 case'
    # The "command"
    foo() {
      printf "stdout\n"
      printf "stderr\n" >&2
      return 0
    }

    Before 'wrapsetup'
    After 'wrapteardown'

    wrapsetup() {
      DEBUG=whynot wrapcmd foo
    }

    wrapteardown() {
      unset DEBUG
    }

    Before 'hooksetup'
    After 'hookteardown'

    hooksetup() {
      pre() {
        printf "pre\n"
      }
      export FOOPREHOOK=pre
    }

    hookteardown() {
      unset FOOPREHOOK
    }

    It 'calls pre hook for foo "command"'
      When call sutfoo
      The status should equal 0
      The stdout should equal "pre
stdout"
      The stderr should equal "stderr"
    End
  End

  Context 'wrapcmd honors post hook in 0 case'
    # The "command"
    foo() {
      printf "stdout\n"
      printf "stderr\n" >&2
      return 0
    }

    Before 'wrapsetup'
    After 'wrapteardown'

    wrapsetup() {
      DEBUG=whynot wrapcmd foo
    }

    wrapteardown() {
      unset DEBUG
    }

    Before 'hooksetup'
    After 'hookteardown'

    hooksetup() {
      post() {
        printf "post\n"
      }
      export FOOPOSTHOOK=post
    }

    hookteardown() {
      unset FOOPOSTHOOK
    }

    It 'calls post hook for foo "command"'
      When call sutfoo
      The status should equal 0
      The stdout should equal "stdout
post"
      The stderr should equal "stderr"
    End
  End

  Context 'enable_tracing() works as intended'
    # To make these tests work we need to "change" time, since nothing acts on
    # the time itself I'm just defining epoch date time to "sut"
    _epoch() { printf "sut"; }
    _pwd() { printf "sut"; }
    _tty() { printf "sut"; }
    _who() { printf "sut"; }

    _trace_cleanup() { return 1; }

    # For now just always tear down the trace directory should be fine even if
    # its missing.
    traceteardown() {
      _clean_trace_dir
    }
    After 'traceteardown'

    timelinecmp() {
      %text
      #|trace enabled at sut for sut.sh
      #|args:
      #|pwd: sut
      #|tty: sut
      #|who: sut
      #|start: sut
    }

    It 'enable_tracing creates what we expect'
      When call enable_tracing sut.sh
      The status should equal 0
      The path "${TRACEDIR}/sut.sh" should be a directory
      The path "${TRACEDIR}/sut.sh/sut" should be a directory
      The path "${TRACEDIR}/sut.sh/sut/timeline" should be a file
      The path "${TRACEDIR}/sut.sh/sut/env" should be a file
      The path "${TRACEDIR}/sut.sh/sut/ps-ef" should be a file
      The path "${TRACEDIR}/sut.sh/sut/uptime" should be a file
      The contents of file "${TRACEDIR}/sut.sh/sut/timeline" should equal "$(timelinecmp)"
    End
  End
End
