# UGREEN CM762 AIC8800 driver — quick reference

See [`INSTALL.md`](INSTALL.md) for detailed installation steps.

## Supported hardware

The UGREEN CM762 identifies itself as USB ID `a69c:8d80` (AIC8800D80 chip)
once switched out of its initial mass-storage mode. `aic_load_fw` already
recognized this ID and carries the matching `aic8800D80` firmware, but the
`aic8800_fdrv` network driver's USB ID table and `aicwf_usb_chipmatch()`
didn't: the device would load firmware but never bind a wireless interface.
`USB_PRODUCT_ID_AIC8800D80` is now registered there too, routed through the
same code path used for the other AIC8800-family USB IDs (D81, D41, D83-D88,
TP-Link/Tenda OEM variants).

## Building the Debian package

```bash
sudo apt install build-essential dkms dpkg-dev linux-headers-$(uname -r)
./build-debian-package.sh
```

Produces `ugreen-cm762-aic8800-dkms_1.4.0_all.deb`.

```bash
sudo dpkg -i ugreen-cm762-aic8800-dkms_1.4.0_all.deb
```

If dependencies are missing: `sudo apt-get install -f`. To remove:
`sudo dpkg -r ugreen-cm762-aic8800-dkms`.

## Kernel compatibility

- 7.2.x: verified on Fedora 44, `7.2.4-200.fc44.x86_64`
- 7.1.x: verified on Fedora 44, `7.1.4-200.fc44.x86_64`
- 6.17.x: targeted; build against the exact distribution headers
- Older kernels: compatibility code remains from the upstream source, not currently tested

Changes selected via `LINUX_VERSION_CODE` at compile time, so one source
tree covers all supported kernels without manual patching:

- 6.x: `in_hardirq()` / timer API changes
- 7.1: several `cfg80211_ops` callbacks (`add_key`, `add_station`, `get_station`, ...) take `struct wireless_dev *` instead of `struct net_device *`; the `struct ieee80211_mgmt` action-frame union layout changed
- 7.2: `remain_on_channel` gained an `rx_addr` parameter; `strncpy()` was removed from the kernel image entirely, so the driver provides its own implementation for its existing call sites

The kernel 7.1 compatibility work was adapted from
[asanrivas/aic8800-linux-driver](https://github.com/asanrivas/aic8800-linux-driver)
(commit `270173e`).

## Manual installation

```bash
sudo make -C drivers/aic8800
sudo make -C drivers/aic8800 install
sudo depmod -a
sudo modprobe aic8800_fdrv

# auto-load on boot
echo "aic8800_fdrv" | sudo tee /etc/modules-load.d/aic8800.conf
```

## Verifying the install

```bash
lsmod | grep aic8800
ip a
sudo dmesg | tail -20
```

A working install shows a new wireless interface (`wlx...`) and a kernel
message: `usbcore: registered new interface driver aic8800_fdrv`.

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

After a kernel update, DKMS should rebuild automatically. If it doesn't:
`sudo dkms autoinstall`.

## Package contents

- `/usr/src/aic8800-1.4.0/` — driver source
- `/etc/modules-load.d/aic8800.conf` — auto-load config
- `/usr/share/doc/ugreen-cm762-aic8800-dkms/` — documentation

## Requirements

- Linux kernel 6.17.x, 7.1.x, or 7.2.x
- DKMS 2.1.0.0 or later
- GCC and matching kernel headers
- USB 2.0/3.0 port

## Driver details

- Module name: `aic8800_fdrv`
- Chipset: AIC8800 (D80 variant)
- Interface: USB
- Device: UGREEN CM762
