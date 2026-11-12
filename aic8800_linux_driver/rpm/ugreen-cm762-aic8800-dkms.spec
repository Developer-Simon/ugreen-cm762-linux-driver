%global dkms_name aic8800

Name:           ugreen-cm762-aic8800-dkms
Version:        1.5.1
Release:        1%{?dist}
Summary:        DKMS driver for the UGREEN CM762 USB Wi-Fi adapter (AIC8800D80)
License:        GPL-2.0-or-later
URL:            https://github.com/Developer-Simon/ugreen-cm762-linux-driver
Source0:        %{dkms_name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       dkms
Requires:       gcc
Requires:       make
Requires:       kernel-devel
# aic.rules ejects the adapter's mass-storage mode with /usr/bin/eject
Requires:       util-linux
Requires(post): dkms
Requires(preun): dkms

%description
Kernel modules aic_load_fw and aic8800_fdrv for the UGREEN CM762 USB Wi-Fi
adapter (AIC8800D80, USB ID a69c:8d80), built through DKMS for every installed
kernel. The package also ships the AIC8800D80 firmware, a udev rule that
switches the adapter out of its mass-storage mode, and a modules-load.d entry
that loads the driver at boot.

%prep
%setup -q -n %{dkms_name}-%{version}

%build
# DKMS builds the modules on the target system.

%install
install -d %{buildroot}%{_usrsrc}/%{dkms_name}-%{version}
cp -a drivers/aic8800/. %{buildroot}%{_usrsrc}/%{dkms_name}-%{version}/

cat > %{buildroot}%{_usrsrc}/%{dkms_name}-%{version}/dkms.conf <<'EOF'
PACKAGE_NAME="%{dkms_name}"
PACKAGE_VERSION="%{version}"
MAKE[0]="make KVER=${kernelver} KDIR=${kernel_source_dir}"
BUILT_MODULE_NAME[0]="aic_load_fw"
BUILT_MODULE_LOCATION[0]="aic_load_fw/"
DEST_MODULE_LOCATION[0]="/extra"
BUILT_MODULE_NAME[1]="aic8800_fdrv"
BUILT_MODULE_LOCATION[1]="aic8800_fdrv/"
DEST_MODULE_LOCATION[1]="/extra"
AUTOINSTALL="yes"
EOF

install -d %{buildroot}%{_prefix}/lib/firmware
cp -a fw/aic8800D80 %{buildroot}%{_prefix}/lib/firmware/

install -Dpm 644 tools/aic.rules %{buildroot}%{_prefix}/lib/udev/rules.d/90-aic8800.rules

install -d %{buildroot}%{_prefix}/lib/modules-load.d
printf 'aic_load_fw\naic8800_fdrv\n' > %{buildroot}%{_prefix}/lib/modules-load.d/aic8800.conf

%post
dkms add -m %{dkms_name} -v %{version} --rpm_safe_upgrade || :
# Build for every kernel that has headers installed; DKMS autoinstall covers
# kernels installed later.
for kdir in /usr/src/kernels/*; do
    [ -e "$kdir/Makefile" ] || continue
    dkms install -m %{dkms_name} -v %{version} -k "$(basename "$kdir")" \
        --kernelsourcedir "$kdir" || :
done
udevadm control --reload >/dev/null 2>&1 || :

%preun
if [ "$1" -eq 0 ]; then
    modprobe -r aic8800_fdrv >/dev/null 2>&1 || :
    modprobe -r aic_load_fw >/dev/null 2>&1 || :
fi
dkms remove -m %{dkms_name} -v %{version} --all --rpm_safe_upgrade || :

%postun
udevadm control --reload >/dev/null 2>&1 || :

%files
%license LICENSE
%doc README.md INSTALL.md
%{_usrsrc}/%{dkms_name}-%{version}/
%{_prefix}/lib/firmware/aic8800D80/
%{_prefix}/lib/udev/rules.d/90-aic8800.rules
%{_prefix}/lib/modules-load.d/aic8800.conf

%changelog
* Thu Nov 12 2026 Developer-Simon <73778205+Developer-Simon@users.noreply.github.com> - 1.5.1-1
- Fix firmware loading from kernel threads on Linux 7.3: the adapter is
  probed from the usb_hub_wq kworker after it re-enumerates, where paths no
  longer resolve against the real root. The firmware is now opened relative
  to init's root, so wlan0 appears at boot without reloading the modules.

* Wed Nov 11 2026 Developer-Simon <73778205+Developer-Simon@users.noreply.github.com> - 1.5.0-1
- Kernel 7.3 support

* Wed Nov 11 2026 Developer-Simon <73778205+Developer-Simon@users.noreply.github.com> - 1.4.0-1
- First RPM packaging; builds against kernels 6.17 through 7.3
