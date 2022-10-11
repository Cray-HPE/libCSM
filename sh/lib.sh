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

# All lib shell should Presume to be run with set -e and set -u. Pipes are and
# should be allowed to fail within this library, pipefile is not portable and
# shouldn't be depended upon for error checking. If a command fails that needs
# to be checked not piped into another command.

# Note in posix shell there is no way to know at source time where one is
# sourced. So we require caller scripts to provide that information in
# $SOURCEPREFIX as executing shells do have that information.

# Note: Order of imports is important, will eventually automate this.
. "${SOURCEPREFIX?}/internal.sh"
. "${SOURCEPREFIX?}/logger.sh"
. "${SOURCEPREFIX?}/cmd.sh"
