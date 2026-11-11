#!/bin/bash
# Build the ugreen-cm762-aic8800-dkms RPM (noarch, DKMS-based).
# Requires: rpm-build. Run from anywhere; output lands in this directory.

set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

SPEC=rpm/ugreen-cm762-aic8800-dkms.spec
NAME=aic8800
VERSION=$(rpmspec -q --qf '%{VERSION}\n' --srpm "$SPEC")
TOPDIR="$(pwd)/rpmbuild"
STAGE="${TOPDIR}/stage/${NAME}-${VERSION}"

command -v rpmbuild >/dev/null || { echo "rpmbuild not found: sudo dnf install rpm-build" >&2; exit 1; }

rm -rf "$TOPDIR"
mkdir -p "$TOPDIR"/{SOURCES,SPECS,RPMS,SRPMS,BUILD} "$STAGE"

# Stage only sources, never local build output.
tar -C . \
    --exclude='*.o' --exclude='*.ko' --exclude='*.mod' --exclude='*.mod.c' \
    --exclude='*.o.d' --exclude='.*.cmd' --exclude='modules.order' \
    --exclude='Module.symvers' --exclude='.tmp_versions' \
    -cf - drivers/aic8800 fw/aic8800D80 tools/aic.rules INSTALL.md README.md \
    | tar -C "$STAGE" -xf -
cp ../LICENSE "$STAGE/"

tar -C "${TOPDIR}/stage" -czf "${TOPDIR}/SOURCES/${NAME}-${VERSION}.tar.gz" "${NAME}-${VERSION}"
cp "$SPEC" "${TOPDIR}/SPECS/"

rpmbuild --define "_topdir ${TOPDIR}" -ba "${TOPDIR}/SPECS/$(basename "$SPEC")"

find "${TOPDIR}/RPMS" "${TOPDIR}/SRPMS" -name '*.rpm' -exec cp {} . \;
rm -rf "$TOPDIR"

echo
ls -1 ./*.rpm
echo
echo "Install: sudo dnf install ./$(ls ugreen-cm762-aic8800-dkms-*.noarch.rpm | head -1)"
