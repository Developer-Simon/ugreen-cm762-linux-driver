/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _AIC_FS_COMPAT_H_
#define _AIC_FS_COMPAT_H_

#include <linux/fs.h>
#include <linux/version.h>

/*
 * Since Linux 7.3 kernel threads (e.g. the usb_hub_wq kworker that probes
 * the adapter after it re-enumerates) resolve paths against an empty nullfs
 * root instead of the real root filesystem. A plain filp_open() of
 * /lib/firmware/... then fails, so the firmware never gets uploaded. Resolve
 * the path against init's root, as the kernel's own firmware loader does.
 */
#if LINUX_VERSION_CODE >= KERNEL_VERSION(7, 3, 0)
#include <linux/fs_struct.h>

static inline struct file *aic_filp_open(const char *path, int flags, umode_t mode)
{
	struct file *fp;

	scoped_with_init_fs()
		fp = filp_open(path, flags, mode);
	return fp;
}
#else
#define aic_filp_open(path, flags, mode) filp_open(path, flags, mode)
#endif

#endif /* _AIC_FS_COMPAT_H_ */
