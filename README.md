# csm-common-library
A library for common for CSM.

# Shell specific notes

As this is library shell and intended to be usable in minimal containers and elsewhere, we want to ensure all shell is usable in any bourne compatible shell. That includes ash, dash, busybox sh, etc. Note c and teco c shells are not included in this definition.

To aide in this we have a github action, https://github.com/luizm/action-sh-checker that will be used to run the following on all pull requests:
- shellcheck
- shfmt
- checkbashisms

This will help to ensure all library code remains portable and consistently formatted and enforced.

To run this action locally against work in progress changes install act https://github.com/nektos/act and/or docker or some other equivalent and run *act -j sh-checker*.

## Shell unit tests

As we want to ensure portability across posix shells, the unit test library of choice is shellspec. For details why go here https://shellspec.info/comparison.html in essence it has more features than bats and also allows us to ensure other shells function.

To locally run tests ensure you have shellspec installed https://github.com/shellspec/shellspec and available locally and you may simply run *shellspec* or *make test* to run all the unit tests. To run against all configured shells known to work run *make test-all*.

If you also have entr https://github.com/eradman/entr installed you can run *make ci* to run against all of the configured shells in the makefile on every update to a shell script.

That will look like so:

```sh
$ make ci
find . -name "*.sh" -type f | entr -d sh -xec "for s in sh bash ksh; do shellspec --shell \$s ; done; date"
+ for s in sh bash ksh
+ shellspec --shell sh
Running: /run/current-system/sw/bin/sh [bash 5.1.16(1)-release]


Finished in 0.19 seconds (user 0.11 seconds, sys 0.06 seconds)
0 examples, 0 failures

+ for s in sh bash ksh
+ shellspec --shell bash
Running: /run/current-system/sw/bin/bash [bash 5.1.16(1)-release]


Finished in 0.17 seconds (user 0.11 seconds, sys 0.06 seconds)
0 examples, 0 failures

+ for s in sh bash ksh
+ shellspec --shell ksh
Running: /bin/ksh [ksh Version AJM 93u+ 2012-08-01]


Finished in 0.07 seconds (user 0.01 seconds, sys 0.00 seconds)
0 examples, 0 failures

+ date
Mon Oct 10 12:15:56 CDT 2022
```

Note this presumes all of the shells are available locally. This will become a github action as well in a future pr.
