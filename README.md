# UGREEN CM762 AIC8800 Linux driver

Patched AIC8800 driver for the UGREEN CM762 USB Wi-Fi adapter. The chip is an
AIC8800D80 (USB ID `a69c:8d80`); the device enumerates in mass-storage mode
first and switches to that ID once usb-modeswitch runs.

Supported kernels: 7.2.x, 7.1.x, and 6.17.x. There are no separate source
trees per kernel; the compatibility code picks the right API at compile time
based on the kernel headers used for the build.

## Installation

### Debian package

```bash
cd aic8800_linux_driver
./build-debian-package.sh
sudo dpkg -i ./ugreen-cm762-aic8800-dkms_1.4.0_all.deb
```

If dependencies are missing: `sudo apt-get install -f`

### From source

```bash
git clone https://github.com/Developer-Simon/ugreen-cm762-linux-driver.git
cd ugreen-cm762-linux-driver/aic8800_linux_driver

sudo make -C drivers/aic8800
sudo make -C drivers/aic8800 install
sudo depmod -a
sudo modprobe aic8800_fdrv
```

To build against a kernel other than the one currently running, pass its
build directory and version:

```bash
TARGET_KERNEL=7.1.0-custom
make -C drivers/aic8800 \
	KDIR=/lib/modules/${TARGET_KERNEL}/build \
	KVER=${TARGET_KERNEL}
```

Check the headers exist first: `test -e /lib/modules/${TARGET_KERNEL}/build/Makefile`.
Modules built against one kernel's headers won't load on another — build and
install separately per kernel, or let DKMS do that automatically on each
kernel update.

## Requirements

- Kernel headers matching the running kernel (`linux-headers-$(uname -r)`)
- build-essential / gcc
- DKMS, for the packaged install

## Verifying the install

```bash
lsmod | grep aic8800
ip a | grep wlx
sudo dmesg | grep -i aic8800
```

A working install shows a `wlx...` interface in `ip a`.

## Kernel compatibility

| Kernel | Status |
| --- | --- |
| 7.2.x | Verified on Fedora 44, `7.2.4-200.fc44.x86_64` |
| 7.1.x | Verified on Fedora 44, `7.1.4-200.fc44.x86_64` |
| 6.17.x | Targeted; build against the exact distribution headers |
| Older | Compatibility code remains from the upstream source, not currently tested |

Relevant changes, selected via `LINUX_VERSION_CODE` at compile time:

- 6.x: `del_timer()` / `del_timer_sync()` → `timer_delete()` / `timer_delete_sync()`; `in_irq()` → `in_hardirq()`
- 7.1: several `cfg80211_ops` callbacks (`add_key`, `add_station`, `get_station`, and others) take `struct wireless_dev *` instead of `struct net_device *`; the `struct ieee80211_mgmt` action-frame union layout changed
- 7.2: `remain_on_channel` gained an `rx_addr` parameter; `strncpy()` was removed from the kernel image entirely, so the driver carries its own implementation for its existing call sites

The kernel 7.1 compatibility work was adapted from
[asanrivas/aic8800-linux-driver](https://github.com/asanrivas/aic8800-linux-driver)
(commit `270173e`).

## Repository layout

```
.
├── aic8800_linux_driver/       driver source
│   ├── drivers/aic8800/        kernel modules (aic8800_fdrv, aic_load_fw)
│   ├── fw/                     firmware
│   ├── build-debian-package.sh
│   └── INSTALL.md
├── docs/vendor/                 vendor PDFs, reference only
├── tools/legacy/                 old Kali header-install scripts
└── release_note.txt
```

## Uninstalling

Debian package:
```bash
sudo dpkg -r ugreen-cm762-aic8800-dkms
```

Manual install:
```bash
sudo modprobe -r aic8800_fdrv aic_load_fw
sudo rm /lib/modules/$(uname -r)/kernel/drivers/net/wireless/aic8800/*.ko
sudo depmod -a
sudo rm /etc/modules-load.d/aic8800.conf
```

## Troubleshooting

No wireless interface after loading the module:
```bash
lsusb | grep -i wireless
sudo dmesg | tail -30
sudo modprobe -r aic8800_fdrv
sudo modprobe aic8800_fdrv
```
Confirm the device shows up as `a69c:8d80` and that dmesg reports something
like "New interface create wlan0". If it doesn't, the driver isn't binding
to the device.

Interface exists but scans return nothing: check for a stray
`wpa_supplicant.service` running independently of NetworkManager
(`systemctl status wpa_supplicant`). If NetworkManager and a separate
supplicant instance both hold the interface, scans can fail with
`SIOCSIWSCAN: Inappropriate ioctl for device` — that's the legacy WEXT API,
which this driver doesn't implement on purpose. Stop the stray service
(`sudo systemctl stop wpa_supplicant`) and let NetworkManager manage the
interface directly.

After a kernel update, DKMS should rebuild automatically. If it doesn't:
`sudo dkms autoinstall`.

## Release workflow

Build packages locally with `aic8800_linux_driver/build-debian-package.sh`.
Generated `.deb` files are release artifacts and are not committed to this
tree. Inspect one with `dpkg-deb --info` and `dpkg-deb --contents` before
publishing.

## License

Based on the original AIC8800 driver, Copyright (C) RivieraWaves 2012-2019.
Kernel 6.17/7.1/7.2 compatibility and CM762 hardware support added in 2026.
GPL v2, see [LICENSE](LICENSE).

Provided as-is; back up your system before installing kernel modules.
