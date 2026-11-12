# UGREEN CM762 AIC8800 Linux driver

[![Build](https://github.com/Developer-Simon/ugreen-cm762-linux-driver/actions/workflows/build.yml/badge.svg)](https://github.com/Developer-Simon/ugreen-cm762-linux-driver/actions/workflows/build.yml)
[![Release](https://img.shields.io/github/v/release/Developer-Simon/ugreen-cm762-linux-driver)](https://github.com/Developer-Simon/ugreen-cm762-linux-driver/releases/latest)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Kernel: 6.17 | 7.1 | 7.2 | 7.3](https://img.shields.io/badge/Kernel-6.17%20%7C%207.1%20%7C%207.2%20%7C%207.3-green.svg)](https://kernel.org/)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://www.linux.org/)

Patched AIC8800 driver for the UGREEN CM762 USB Wi-Fi adapter. The chip is an
AIC8800D80. The adapter first shows up as a USB mass-storage device and
switches to its Wi-Fi ID, `a69c:8d80`, once a udev rule ejects that storage
device.

Supported kernels are 7.3.x, 7.2.x, 7.1.x and 6.17.x.

## Installation

Each [GitHub release](https://github.com/Developer-Simon/ugreen-cm762-linux-driver/releases/latest)
has a `.rpm` for Fedora and a `.deb` for Debian and Ubuntu. Both are DKMS
packages: they contain the driver source, compile the modules on your machine
during installation, and rebuild them automatically after every kernel update.

### Fedora

```bash
curl -LO https://github.com/Developer-Simon/ugreen-cm762-linux-driver/releases/download/v1.5.1/ugreen-cm762-aic8800-dkms-1.5.1-1.fc44.noarch.rpm
sudo dnf install ./ugreen-cm762-aic8800-dkms-1.5.1-1.fc44.noarch.rpm
```

dnf pulls in `dkms`, `kernel-devel`, `gcc` and `make`, then builds the modules
for every installed kernel that has headers. The package also installs the
AIC8800D80 firmware to `/usr/lib/firmware/aic8800D80`, the udev rule that ejects
the mass-storage mode, and a `modules-load.d` entry so the driver loads at boot.
Unplug and replug the adapter once after installing.

### Debian and Ubuntu

```bash
sudo apt install dkms build-essential linux-headers-$(uname -r)
curl -LO https://github.com/Developer-Simon/ugreen-cm762-linux-driver/releases/download/v1.5.1/ugreen-cm762-aic8800-dkms_1.5.1_all.deb
sudo dpkg -i ./ugreen-cm762-aic8800-dkms_1.5.1_all.deb
```

If dpkg reports missing dependencies, run `sudo apt-get install -f`.

The `.deb` does not install the firmware or the udev rule. Get them from the
source tree:

```bash
git clone https://github.com/Developer-Simon/ugreen-cm762-linux-driver.git
cd ugreen-cm762-linux-driver/aic8800_linux_driver
./install_setup.sh
```

### Which release for which kernel

| Release | Kernels |
| --- | --- |
| v1.5.1 | 6.17, 7.1, 7.2, 7.3 |
| v1.4.0 | 6.17, 7.1, 7.2 |

Use the latest release unless you have a reason not to.

## Verifying the install

```bash
dkms status aic8800
lsmod | grep aic8800
ip -br link
sudo dmesg | grep -i aic8800
```

`dkms status` should list the driver as `installed` for your running kernel, and
`ip -br link` should show a new wireless interface (`wlan0` or `wlx...`).

## Updating

Kernel updates need no action: DKMS builds the modules for the new kernel when
it is installed. To move to a newer driver release, install the newer package
the same way as above. dnf and dpkg replace the old version and its DKMS
builds.

## Uninstalling

```bash
sudo dnf remove ugreen-cm762-aic8800-dkms   # Fedora
sudo dpkg -r ugreen-cm762-aic8800-dkms      # Debian and Ubuntu
```

Both commands also remove the DKMS builds for all kernels.

## Troubleshooting

If no wireless interface appears:
```bash
lsusb | grep -i a69c
dkms status aic8800
sudo dmesg | tail -30
sudo modprobe -r aic8800_fdrv
sudo modprobe aic8800_fdrv
```
The adapter should be listed as `a69c:8d80`. If it shows a different
`a69c:` ID, it is still in mass-storage mode and the udev rule did not run;
replug it. If dmesg has no line like "New interface create wlan0", the driver
is not binding to the device.

If `dkms status` shows the driver only as `added` or `built` for your kernel,
the build failed or the headers for that kernel are missing. Install the
headers (`kernel-devel` or `linux-headers-$(uname -r)`) and run
`sudo dkms autoinstall`.

If the interface exists but scans return nothing, check whether a separate
`wpa_supplicant.service` is running next to NetworkManager
(`systemctl status wpa_supplicant`). When both hold the interface, scans can
fail with `SIOCSIWSCAN: Inappropriate ioctl for device`. That error comes from
the legacy WEXT API, which this driver deliberately doesn't implement. Stop the
extra service with `sudo systemctl stop wpa_supplicant` and let NetworkManager
manage the interface.

## Kernel compatibility

| Kernel | Status |
| --- | --- |
| 7.3.x | Tested on Fedora 44, `7.3.3-200.fc44.x86_64` |
| 7.2.x | Tested on Fedora 44, `7.2.4-200.fc44.x86_64` |
| 7.1.x | Tested on Fedora 44, `7.1.4-200.fc44.x86_64` |
| 6.17.x | Supported in the code; build against your distribution's exact headers |
| Older | The upstream compatibility code is still there but untested |

All kernels build from the same source tree. The code selects between these
kernel API changes with `LINUX_VERSION_CODE`, based on the headers it is
compiled against:

- 6.x: `del_timer()` and `del_timer_sync()` were replaced by `timer_delete()` and `timer_delete_sync()`, and `in_irq()` by `in_hardirq()`.
- 7.1: several `cfg80211_ops` callbacks (`add_key`, `add_station`, `get_station` and others) take `struct wireless_dev *` instead of `struct net_device *`. The action-frame union in `struct ieee80211_mgmt` also changed layout.
- 7.2: `remain_on_channel` has a new `rx_addr` parameter. `strncpy()` is gone from the kernel, so the driver ships its own version for the places that still call it.
- 7.3: cfg80211 allocates cookies itself and passes them to `mgmt_tx` and `remain_on_channel` by value. `probe_client` was renamed to `probe_peer`, and `cfg80211_probe_status()` takes an extra `link_id` argument.

The kernel 7.1 changes were adapted from
[asanrivas/aic8800-linux-driver](https://github.com/asanrivas/aic8800-linux-driver)
(commit `270173e`).

## Building manually

You only need this to test unreleased changes or to build for a distribution
without a matching package.

### Building the packages yourself

```bash
git clone https://github.com/Developer-Simon/ugreen-cm762-linux-driver.git
cd ugreen-cm762-linux-driver/aic8800_linux_driver

# Fedora, needs rpm-build
./build-rpm-package.sh

# Debian and Ubuntu, needs dpkg-dev
./build-debian-package.sh
```

The packages land in `aic8800_linux_driver/` and install the same way as the
release downloads.

### Building the modules without a package

```bash
cd ugreen-cm762-linux-driver/aic8800_linux_driver
make -C drivers/aic8800
sudo make -C drivers/aic8800 install
sudo depmod -a
./install_setup.sh   # firmware and udev rule
sudo modprobe aic8800_fdrv
```

This builds for the running kernel only and is not rebuilt after kernel
updates. To build for another installed kernel, pass its build directory and
version:

```bash
TARGET_KERNEL=7.1.0-custom
make -C drivers/aic8800 \
	KDIR=/lib/modules/${TARGET_KERNEL}/build \
	KVER=${TARGET_KERNEL}
```

A module built against one kernel's headers won't load on another kernel.

To remove a manual install:
```bash
sudo modprobe -r aic8800_fdrv aic_load_fw
sudo make -C drivers/aic8800 uninstall
./uninstall_setup.sh
```

## Releases and CI

`.github/workflows/build.yml` compiles the modules on every push and pull
request that touches the driver, against Ubuntu's kernel headers and against
the current Fedora 44 `kernel-devel`.

`.github/workflows/release.yml` runs on every push to `main`. It reads the
package version from `build-debian-package.sh` and from the RPM spec, and
fails if the two differ. If no release exists for that version yet, it runs
the compile check, builds the `.deb` and the `.rpm`, and publishes both as
release `v<version>`. Pushes that don't change the version do nothing.

To publish a release, bump the version in both files (and add a `%changelog`
entry to the spec) in the pull request; merging it to `main` creates the
release. Running the workflow by hand rebuilds the packages for the current
version and replaces the files on its existing release.

Built packages are not committed to the repository.

## Repository layout

```
.
├── .github/workflows/          compile check and release packaging
├── aic8800_linux_driver/       driver source
│   ├── drivers/aic8800/        kernel modules (aic8800_fdrv, aic_load_fw)
│   ├── fw/                     firmware
│   ├── rpm/                    RPM spec file
│   ├── tools/aic.rules         udev rule for the mass-storage switch
│   ├── build-debian-package.sh
│   ├── build-rpm-package.sh
│   └── INSTALL.md
├── docs/vendor/                vendor PDFs, reference only
├── tools/legacy/               old Kali header-install scripts
└── release_note.txt            vendor release notes
```

## License

Based on the original AIC8800 driver, Copyright (C) RivieraWaves 2012-2019.
Kernel 6.17, 7.1, 7.2 and 7.3 compatibility and CM762 hardware support were
added in 2026. Licensed under GPL v2, see [LICENSE](LICENSE).

The driver is provided as is. Back up your system before installing kernel
modules.
