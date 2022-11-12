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

# All lib shell should Presume to be run with set -e and set -u. Pipes are and
# should be allowed to fail within this library, pipefile is not portable and
# shouldn't be depended upon for error checking. If a command fails that needs
# to be checked not piped into another command.

# Note in posix shell there is no way to know at source time where one is
# sourced from a sourced file. So we require caller scripts to provide that
# information in $SOURCEPREFIX as executing shells do have that information.
#
# Yes BASH_SOURCE allows this, but that doesn't work on dash, or ash, or
# anything other than bash and our intent here is to run in busybox containers
# as well as ubuntu.

# Note: Order of imports is important, will eventually automate this.
if [ -n "${SOURCEPREFIX}" ]; then
  . "${SOURCEPREFIX}/internal.sh"
  . "${SOURCEPREFIX}/logger.sh"
  . "${SOURCEPREFIX}/cmd.sh"
  . "${SOURCEPREFIX}/yaml.sh"

  # Don't import lib.sh directly in shellspec tests, this is why.
  trap libcleanup EXIT
else
  # Nothing will be sourced in this case
  printf "You must set SOURCEPREFIX to the base directory of lib.sh in before sourcing this library!\n" >&2
fi
