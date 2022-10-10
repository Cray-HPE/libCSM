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
