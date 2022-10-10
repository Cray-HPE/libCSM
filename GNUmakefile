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

# Import Makefile so this is transparent. Don't have time to improve that at the moment.
ifneq ("$(wildcard Makefile)","")
  $(info importing Makefile)
  include Makefile
endif

# This is for ci/testing/unit testing
SHELLSPEC:=shellspec

# Might want to run with parallelism by default to make sure people don't
# introduce dependencies in tests and with randomness.
# SHELLSEPCARGS:=--jobs 4
SHELLSEPCARGS:=
ENTR:=entr
SH:=sh
BASH:=bash
KSH:=ksh
SHELLS:=$(SH) $(BASH) $(KSH)
DATE:=date

# Quick run shellspec to do a one off test
.PHONY: test
test:
	$(SHELLSPEC)

# Run tests against all the shell intepreters in SHELLS
.PHONY: test-all
test-all:
	set -xe; for s in $(SHELLS); do $(SHELLSPEC) --shell $$s $(SHELLSPECARGS); done;

# For development, validate the shell under test is actually portable and can
# run within say busybox sh or dash and not just bash.
#
# Good shell shouldn't care what bourne interpreter its running within and
# ensures we can run in a busybox/alpine linux container easy peasy lemon
# squeezy if needed.
.PHONY: ci
ci:
	find . -name "*.sh" -type f | $(ENTR) -d sh -xec "for s in $(SHELLS); do $(SHELLSPEC) --shell \$$s $(SHELLSPECARGS); done; $(DATE)"
