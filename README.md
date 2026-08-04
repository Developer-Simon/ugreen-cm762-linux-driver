# UGREEN CM762 USB Wireless Adapter Driver for Linux Kernels 6.17 and 7.1

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Kernel: 6.17 and 7.1](https://img.shields.io/badge/Kernel-6.17%20%7C%207.1-green.svg)](https://kernel.org/)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://www.linux.org/)

Patched AIC8800 driver for the UGREEN CM762 USB Wireless Adapter. The current
support target is Linux 6.17 and 7.1; each build must use the exact headers for
the kernel that will load the modules.

## 🎯 Features

- ✅ **Kernel 6.17 and 7.1 source compatibility** - Version-specific APIs are selected at compile time
- ✅ **DKMS Integration** - Automatic rebuild on kernel updates
- ✅ **Debian Package** - Easy installation with `.deb` package
- ✅ **Auto-load on Boot** - Driver loads automatically after installation
- ✅ **Clean Uninstall** - Proper removal with all files cleaned up

## Quick Installation

## Selecting the Kernel Build

There are no separate 6.17 and 7.1 driver source trees. The compatibility code
selects the kernel API at compile time from the kernel headers used by the build.
Choose the target kernel by choosing its matching headers:

| Target kernel | Build against |
| --- | --- |
| Linux 6.17 | `/lib/modules/6.17.x-.../build` |
| Linux 7.1 | `/lib/modules/7.1.x-.../build` |

### Support Status

| Kernel series | Status |
| --- | --- |
| Linux 7.1.x | Source compatibility and build verified on Fedora 44 with `7.1.4-200.fc44.x86_64` and matching `kernel-devel` |
| Linux 6.17.x | Source compatibility is targeted; build against the exact distribution headers before installation |
| Older kernels | Compatibility branches remain in the inherited source, but they are not current tested support |

For the currently running kernel, install its matching headers and build normally:

```bash
sudo apt install build-essential linux-headers-$(uname -r)
make -C drivers/aic8800
```

To build for another installed kernel, pass its kernel build directory and version:

```bash
TARGET_KERNEL=7.1.0-custom
make -C drivers/aic8800 \
	KDIR=/lib/modules/${TARGET_KERNEL}/build \
	KVER=${TARGET_KERNEL}
```

Replace `TARGET_KERNEL` with the exact 6.17 kernel version to build the 6.17
variant. Confirm that the target headers exist before starting:

```bash
test -e /lib/modules/${TARGET_KERNEL}/build/Makefile
```

Do not build on 6.17 and then install those modules into 7.1, or the reverse.
Build and install separately for each target kernel. DKMS handles this automatically:
one source package is rebuilt once per installed kernel using that kernel's headers.

### Option 1: Build from Source

```bash
# Clone the repository
git clone https://github.com/morjaradat/ugreen-cm762-linux-driver.git
cd ugreen-cm762-linux-driver/aic8800_linux_driver

# Build
sudo make -C drivers/aic8800

# Install
sudo make -C drivers/aic8800 install

# Load module
sudo depmod -a
sudo modprobe aic8800_fdrv
```

### Option 2: Build a Debian Package

```bash
cd aic8800_linux_driver
./build-debian-package.sh
# Install the generated package when ready
sudo dpkg -i ./ugreen-cm762-aic8800-dkms_1.4.0_all.deb
```

## 📋 System Requirements

- Linux kernel 6.17.x or 7.1.x for the current support target
- GCC compiler
- Linux kernel headers: `sudo apt install linux-headers-$(uname -r)`
- DKMS (for package installation): `sudo apt install dkms`
- Build tools: `sudo apt install build-essential`

## 🔍 Verification

After installation, verify the driver is working:

```bash
# Check module is loaded
lsmod | grep aic8800

# Check wireless interface
ip a | grep wlx

# View kernel messages
sudo dmesg | grep -i aic8800
```

You should see a new wireless interface (e.g., `wlxc83a35c64045`).

## 🛠️ Supported Hardware

- **Device:** UGREEN CM762 USB Wireless Adapter
- **Chipset:** AIC8800
- **Interface:** USB 2.0 / USB 3.0
- **Vendor ID:** Check with `lsusb`

## 📦 What's Included

```
.
├── aic8800_linux_driver/           # Main driver source
│   ├── drivers/aic8800/            # Kernel modules
│   │   ├── aic8800_fdrv/          # Main driver module
│   │   └── aic_load_fw/           # Firmware loader
│   ├── fw/                        # Firmware files
│   ├── build-debian-package.sh    # Debian package builder
│   ├── README.md                  # Quick reference
│   └── INSTALL.md                 # Installation guide
├── docs/vendor/                   # Historical vendor references
├── tools/legacy/                  # Historical Kali header helpers
└── release_note.txt               # Release notes
```

## 🔧 Kernel Compatibility Patches

The compatibility work covers the current 6.17 and 7.1 targets. The 6.x and
7.1 changes are selected from `LINUX_VERSION_CODE` during compilation:

### Timer API Updates
- `del_timer()` → `timer_delete()`
- `del_timer_sync()` → `timer_delete_sync()`
- `from_timer()` → `container_of()` macro

### cfg80211 Wireless API
- Updated `cfg80211_rx_spurious_frame()` with `sme` parameter
- Updated `cfg80211_rx_unexpected_4addr_frame()` with `sme` parameter
- Disabled incompatible callback functions in `cfg80211_ops`

### Linux 7.1 API Changes
- Updated `cfg80211_ops` callbacks to use `struct wireless_dev *` where required
- Updated action-frame handling for the changed `struct ieee80211_mgmt` layout
- Replaced the incompatible `in_irq()` check with `in_hardirq()`

### Headers
- Added `<linux/version.h>` for version checking
- Added `<linux/timer.h>` for timer functions
- Proper include ordering for compatibility

## 📖 Documentation

- [**README.md**](aic8800_linux_driver/README.md) - Quick reference guide
- [**INSTALL.md**](aic8800_linux_driver/INSTALL.md) - Detailed installation instructions
- [**Release notes**](release_note.txt) - Historical driver releases

## 🗑️ Uninstallation

### Debian Package:
```bash
sudo dpkg -r ugreen-cm762-aic8800-dkms
```

### Manual Installation:
```bash
sudo modprobe -r aic8800_fdrv aic_load_fw
sudo rm /lib/modules/$(uname -r)/kernel/drivers/net/wireless/aic8800/*.ko
sudo depmod -a
sudo rm /etc/modules-load.d/aic8800.conf
```

## 🐛 Troubleshooting

### Driver not loading?
```bash
# Check USB device
lsusb | grep -i wireless

# Check kernel logs
sudo dmesg | tail -30

# Manually load module
sudo modprobe aic8800_fdrv
```

### No wireless interface?
```bash
# Reload module
sudo modprobe -r aic8800_fdrv
sudo modprobe aic8800_fdrv

# Check interface
ip link show
```

### After kernel update?
```bash
# DKMS should auto-rebuild, but you can force it:
sudo dkms autoinstall
sudo dkms status | grep aic8800
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for contribution:
- Testing on different kernel versions
- Support for additional AIC8800 devices
- Bug fixes and improvements
- Documentation enhancements

## 📝 License

This driver is based on the original AIC8800 driver:
- Original: Copyright (C) RivieraWaves 2012-2019
- Kernel 6.17 and 7.1 compatibility work: 2026

Licensed under GPL v2.0 - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This driver is provided "as-is" without warranty of any kind. Use at your own risk.
Always backup your system before installing kernel drivers.

## Release Workflow

Build packages locally with `aic8800_linux_driver/build-debian-package.sh`. Generated
`.deb` files are release artifacts and are intentionally not committed to this source
tree. Inspect a package with `dpkg-deb --info` and `dpkg-deb --contents` before publishing it.

## 📊 Tested On

- Testing is documented in the release notes; verify the running kernel headers before building.

## 🌟 Credits

- Original driver by RivieraWaves
- Kernel 6.17 and 7.1 compatibility patches
- UGREEN hardware support

## 📞 Support

For issues and questions, check the installation guide, driver build output, and kernel logs.
- Review kernel logs: `sudo dmesg | grep aic8800`

---

**Made with ❤️ for the Linux community**
