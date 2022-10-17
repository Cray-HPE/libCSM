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

# Where we store all our temp dirs/files for anything this lib does.
RUNDIR="${RUNDIR:-${TMPDIR:-/tmp}/csm-common-lib-$$}"

# Callers of this script need to call this in an exit handler or temp files
# created will not be cleaned up.
#
# e.g. trap libcleanup EXIT in the calling script
libcleanup() {
  ${RM:-rm} -fr "${RUNDIR}"
}

# Simple wrapper to ensure our rundir is setup. Internal though anyone can call
# it.
mkrundir() {
  install -dm755 "${RUNDIR}"
}

# Create a tempfile using ${RUNDIR} as the prefix, pass in an arg of what the
# files prefix name should be. The intended interface for script users.
libtmpfile() {
  prefix="${1:-caller-did-not-pick-a-name}"
  mkrundir
  tmpfile=$(mktemp -p "${RUNDIR}" "${prefix}-XXXXXXXX")
  rc=$?
  echo "${tmpfile}"
  return "${rc}"
}
