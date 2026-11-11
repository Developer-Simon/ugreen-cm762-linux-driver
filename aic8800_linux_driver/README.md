# UGREEN CM762 AIC8800 driver quick reference

Detailed installation steps are in [`INSTALL.md`](INSTALL.md).

## Supported hardware

Once it leaves its initial mass-storage mode, the UGREEN CM762 reports USB ID
`a69c:8d80` (AIC8800D80 chip). Both modules recognize this ID: `aic_load_fw`
loads the matching `aic8800D80` firmware, and `aic8800_fdrv` lists
`USB_PRODUCT_ID_AIC8800D80` in its USB ID table and in `aicwf_usb_chipmatch()`.
In `aic8800_fdrv` it goes through the same code path as the other AIC8800
family USB IDs (D81, D41, D83 to D88, and the TP-Link and Tenda OEM variants).

## Building the RPM package (Fedora)

```bash
sudo dnf install rpm-build
./build-rpm-package.sh
```

This produces `ugreen-cm762-aic8800-dkms-1.4.0-1.<dist>.noarch.rpm` and a
matching source RPM. The spec file is `rpm/ugreen-cm762-aic8800-dkms.spec`.

```bash
sudo dnf install ./ugreen-cm762-aic8800-dkms-1.4.0-1.fc44.noarch.rpm
```

Besides the DKMS source, the RPM installs the firmware to
`/usr/lib/firmware/aic8800D80`, the udev rule that ejects the mass-storage mode,
and `/usr/lib/modules-load.d/aic8800.conf`. To remove it, run
`sudo dnf remove ugreen-cm762-aic8800-dkms`.

## Building the Debian package

```bash
sudo apt install build-essential dkms dpkg-dev linux-headers-$(uname -r)
./build-debian-package.sh
```

This produces `ugreen-cm762-aic8800-dkms_1.4.0_all.deb`.

```bash
sudo dpkg -i ugreen-cm762-aic8800-dkms_1.4.0_all.deb
```

If dependencies are missing, run `sudo apt-get install -f`. To remove the
package, run `sudo dpkg -r ugreen-cm762-aic8800-dkms`.

Tagged releases build both packages in CI and attach them to the GitHub
release; see the release workflow section in the top-level README.

## Kernel compatibility

- 7.3.x: tested on Fedora 44, `7.3.3-200.fc44.x86_64`
- 7.2.x: tested on Fedora 44, `7.2.4-200.fc44.x86_64`
- 7.1.x: tested on Fedora 44, `7.1.4-200.fc44.x86_64`
- 6.17.x: supported in the code; build against your distribution's exact headers
- Older kernels: the upstream compatibility code is still there but untested

The code selects between these kernel API changes with `LINUX_VERSION_CODE` at
compile time:

- 6.x: `in_hardirq()` and the new timer API
- 7.1: several `cfg80211_ops` callbacks (`add_key`, `add_station`, `get_station` and others) take `struct wireless_dev *` instead of `struct net_device *`. The action-frame union in `struct ieee80211_mgmt` also changed layout.
- 7.2: `remain_on_channel` has a new `rx_addr` parameter. `strncpy()` is gone from the kernel, so the driver ships its own version for the places that still call it.
- 7.3: cfg80211 allocates cookies itself and passes them to `mgmt_tx` and `remain_on_channel` by value. `probe_client` was renamed to `probe_peer`, and `cfg80211_probe_status()` takes an extra `link_id` argument.

The kernel 7.1 changes were adapted from
[asanrivas/aic8800-linux-driver](https://github.com/asanrivas/aic8800-linux-driver)
(commit `270173e`).

## Manual installation

```bash
sudo make -C drivers/aic8800
sudo make -C drivers/aic8800 install
sudo depmod -a
sudo modprobe aic8800_fdrv

# load on boot
echo "aic8800_fdrv" | sudo tee /etc/modules-load.d/aic8800.conf
```

## Verifying the install

```bash
lsmod | grep aic8800
ip a
sudo dmesg | tail -20
```

After a successful install there is a new wireless interface (`wlx...`), and
the kernel log contains `usbcore: registered new interface driver aic8800_fdrv`.

## Troubleshooting

No wireless interface after installation:
```bash
lsusb | grep -i wireless
sudo modprobe aic8800_fdrv
sudo dmesg | grep -i aic8800
```

Module not found:
```bash
sudo dkms status
sudo dkms install aic8800/1.4.0
```

DKMS rebuilds the modules after a kernel update. If that didn't happen, run
`sudo dkms autoinstall`.

## Package contents

Both packages:

- `/usr/src/aic8800-1.4.0/`: driver source for DKMS

Debian package:

- `/etc/modules-load.d/aic8800.conf`: loads the driver at boot
- `/usr/share/doc/ugreen-cm762-aic8800-dkms/`: documentation

RPM package:

- `/usr/lib/modules-load.d/aic8800.conf`: loads the driver at boot
- `/usr/lib/firmware/aic8800D80/`: firmware
- `/usr/lib/udev/rules.d/90-aic8800.rules`: ejects the mass-storage mode
- `/usr/share/doc/ugreen-cm762-aic8800-dkms/`: documentation

## Requirements

- Linux kernel 6.17.x, 7.1.x, 7.2.x or 7.3.x
- DKMS 2.1.0.0 or later
- gcc and headers for the target kernel
- A USB 2.0 or 3.0 port

## Driver details

- Module name: `aic8800_fdrv`
- Chipset: AIC8800 (D80 variant)
- Interface: USB
- Device: UGREEN CM762
