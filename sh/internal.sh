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
