# UGREEN CM762 AIC8800 Linux driver

[![Build](https://github.com/Developer-Simon/ugreen-cm762-linux-driver/actions/workflows/build.yml/badge.svg)](https://github.com/Developer-Simon/ugreen-cm762-linux-driver/actions/workflows/build.yml)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Kernel: 6.17 | 7.1 | 7.2 | 7.3](https://img.shields.io/badge/Kernel-6.17%20%7C%207.1%20%7C%207.2%20%7C%207.3-green.svg)](https://kernel.org/)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://www.linux.org/)

Patched AIC8800 driver for the UGREEN CM762 USB Wi-Fi adapter. The chip is an
AIC8800D80. The adapter first shows up as a USB mass-storage device and
switches to its Wi-Fi ID, `a69c:8d80`, once the udev rule ejects that storage
device.

Supported kernels are 7.3.x, 7.2.x, 7.1.x and 6.17.x. All of them build from
the same source tree: the compatibility code picks the right kernel API at
compile time from the headers you build against.

## Installation

Prebuilt `.deb` and `.rpm` packages are attached to each
[GitHub release](https://github.com/Developer-Simon/ugreen-cm762-linux-driver/releases).
Both are DKMS packages, so the modules are compiled on your machine and
rebuilt automatically after kernel updates.

### Fedora (RPM)

```bash
sudo dnf install ./ugreen-cm762-aic8800-dkms-1.4.0-1.fc44.noarch.rpm
```

dnf pulls in `dkms`, `kernel-devel`, `gcc` and `make`. The package also
installs the AIC8800D80 firmware under `/usr/lib/firmware/aic8800D80`, the udev
rule that ejects the mass-storage mode, and a `modules-load.d` entry so the
driver loads at boot.

To build the RPM yourself:

```bash
sudo dnf install rpm-build
cd aic8800_linux_driver
./build-rpm-package.sh
```

### Debian and Ubuntu (DEB)

```bash
cd aic8800_linux_driver
./build-debian-package.sh
sudo dpkg -i ./ugreen-cm762-aic8800-dkms_1.4.0_all.deb
```

If dpkg reports missing dependencies, run `sudo apt-get install -f`.

### From source

```bash
git clone https://github.com/Developer-Simon/ugreen-cm762-linux-driver.git
cd ugreen-cm762-linux-driver/aic8800_linux_driver

sudo make -C drivers/aic8800
sudo make -C drivers/aic8800 install
sudo depmod -a
sudo modprobe aic8800_fdrv
```

A source install does not include the firmware or the udev rule; run
`./install_setup.sh` for those.

To build for a kernel other than the running one, pass its build directory and
version:

```bash
TARGET_KERNEL=7.1.0-custom
make -C drivers/aic8800 \
	KDIR=/lib/modules/${TARGET_KERNEL}/build \
	KVER=${TARGET_KERNEL}
```

Check that the headers exist first with
`test -e /lib/modules/${TARGET_KERNEL}/build/Makefile`. A module built against
one kernel's headers won't load on another kernel, so either build and install
once per kernel or use one of the DKMS packages.

## Requirements

- Headers for the kernel you build against (`kernel-devel` on Fedora,
  `linux-headers-$(uname -r)` on Debian and Ubuntu)
- gcc and make
- DKMS, for the packaged installs

## Verifying the install

```bash
lsmod | grep aic8800
ip a | grep wlx
sudo dmesg | grep -i aic8800
```

After a successful install, `ip a` lists a `wlx...` interface.

## Kernel compatibility

| Kernel | Status |
| --- | --- |
| 7.3.x | Tested on Fedora 44, `7.3.3-200.fc44.x86_64` |
| 7.2.x | Tested on Fedora 44, `7.2.4-200.fc44.x86_64` |
| 7.1.x | Tested on Fedora 44, `7.1.4-200.fc44.x86_64` |
| 6.17.x | Supported in the code; build against your distribution's exact headers |
| Older | The upstream compatibility code is still there but untested |

The code selects between these kernel API changes with `LINUX_VERSION_CODE`:

- 6.x: `del_timer()` and `del_timer_sync()` were replaced by `timer_delete()` and `timer_delete_sync()`, and `in_irq()` by `in_hardirq()`.
- 7.1: several `cfg80211_ops` callbacks (`add_key`, `add_station`, `get_station` and others) take `struct wireless_dev *` instead of `struct net_device *`. The action-frame union in `struct ieee80211_mgmt` also changed layout.
- 7.2: `remain_on_channel` has a new `rx_addr` parameter. `strncpy()` is gone from the kernel, so the driver ships its own version for the places that still call it.
- 7.3: cfg80211 allocates cookies itself and passes them to `mgmt_tx` and `remain_on_channel` by value. `probe_client` was renamed to `probe_peer`, and `cfg80211_probe_status()` takes an extra `link_id` argument.

The kernel 7.1 changes were adapted from
[asanrivas/aic8800-linux-driver](https://github.com/asanrivas/aic8800-linux-driver)
(commit `270173e`).

## Repository layout

```
.
├── .github/workflows/          CI build check and release packaging
├── aic8800_linux_driver/       driver source
│   ├── drivers/aic8800/        kernel modules (aic8800_fdrv, aic_load_fw)
│   ├── fw/                     firmware
│   ├── rpm/                    RPM spec file
│   ├── build-debian-package.sh
│   ├── build-rpm-package.sh
│   └── INSTALL.md
├── docs/vendor/                 vendor PDFs, reference only
├── tools/legacy/                 old Kali header-install scripts
└── release_note.txt
```

## Uninstalling

RPM package:
```bash
sudo dnf remove ugreen-cm762-aic8800-dkms
```

Debian package:
```bash
sudo dpkg -r ugreen-cm762-aic8800-dkms
```

Source install:
```bash
sudo modprobe -r aic8800_fdrv aic_load_fw
sudo rm /lib/modules/$(uname -r)/kernel/drivers/net/wireless/aic8800/*.ko
sudo depmod -a
sudo rm /etc/modules-load.d/aic8800.conf
```

## Troubleshooting

If no wireless interface appears after loading the module:
```bash
lsusb | grep -i wireless
sudo dmesg | tail -30
sudo modprobe -r aic8800_fdrv
sudo modprobe aic8800_fdrv
```
The adapter should be listed as `a69c:8d80`, and dmesg should contain a line
like "New interface create wlan0". If neither shows up, the driver is not
binding to the device.

If the interface exists but scans return nothing, check whether a separate
`wpa_supplicant.service` is running next to NetworkManager
(`systemctl status wpa_supplicant`). When both hold the interface, scans can
fail with `SIOCSIWSCAN: Inappropriate ioctl for device`. That error comes from
the legacy WEXT API, which this driver deliberately doesn't implement. Stop the
extra service with `sudo systemctl stop wpa_supplicant` and let NetworkManager
manage the interface.

DKMS rebuilds the modules after a kernel update. If that didn't happen, run
`sudo dkms autoinstall`.

## Release workflow

Every push and pull request that touches the driver runs
`.github/workflows/build.yml`, which compiles the modules against Ubuntu's
kernel headers and against the current Fedora 44 `kernel-devel`.

Pushing a tag such as `v1.4.0` runs `.github/workflows/release.yml`. It runs
the same compile check first, then builds the `.deb` on Ubuntu and the `.rpm` in a Fedora 44 container, then attaches
both to the GitHub release for that tag. The tag has to start with the package
version from `build-debian-package.sh` and the RPM spec (`v1.4.0` or
`v1.4.0-something`), otherwise the job fails. Bump the version in both files
before tagging. To rebuild the packages for an existing tag, run the workflow
by hand and enter the tag.

Built packages are not committed to the repository.

## License

Based on the original AIC8800 driver, Copyright (C) RivieraWaves 2012-2019.
Kernel 6.17, 7.1, 7.2 and 7.3 compatibility and CM762 hardware support were
added in 2026. Licensed under GPL v2, see [LICENSE](LICENSE).

The driver is provided as is. Back up your system before installing kernel
modules.
