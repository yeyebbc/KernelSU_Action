# KernelSU Action — Xperia XZ2 Premium

**中文** | [English](README_EN.md)

为 Sony Xperia XZ2 Premium **H8116**（`aurora`）构建包含 [backslashxx/KernelSU](https://github.com/backslashxx/KernelSU) 的 **boot.img**。目标系统为 **LineageOS 22 / Android 15**，内核版本为 **4.9.337-perf+**。不再生成 AnyKernel3 刷机包。

## 使用

1. 将当前系统的 boot 镜像放在 `h8116-lineage/boot.img`，匹配的 DTBO 放在 `h8116-lineage/dtbo.img`。工作流直接使用仓库内的镜像，不下载其他设备的 boot 镜像。
2. 将仓库和镜像推送至自己的 GitHub fork。在 **Actions** 中选择 H8116 构建工作流，点击 **Run workflow**。
3. 构建成功后下载并解压镜像 artifact，取得 `boot.img`。同时提供原样复制的 `dtbo.img`、构建来源记录和内核配置。
4. 安装 [backslashxx/KernelSU releases](https://github.com/backslashxx/KernelSU/releases) 中匹配的 Manager，不使用官方 KernelSU Manager。

`config.env` 配置 Sony 内核源码、版本和工具链。设备使用 [LineageOS Sony SDM845 内核](https://github.com/LineageOS/android_kernel_sony_sdm845/tree/lineage-22.2) 的 `tama_aurora_defconfig`。KernelSU 内建于内核，启用该 fork 针对 Linux 4.9 的系统调用表 hook 模式，不再应用旧版官方 KernelSU 手动补丁。

工作流启用并检查 `CONFIG_DEBUG_INFO_DWARF4=y`，保留调试信息，同时避免 Clang 19 默认生成的 DWARF 5 指令与 GCC 4.9 预编译工具链中的旧汇编器不兼容。

## 镜像处理

`scripts/repack_boot.py` 使用 AOSP `unpack_bootimg.py` 和 `mkbootimg.py`，仅以编译得到的 `Image.gz-dtb` 替换内核。保留原镜像中的 recovery ramdisk、命令行、系统版本和安全补丁日期、加载地址及其他非内核数据，并在重新打包后逐项验证。

提供的 boot 镜像为 header v1、4096 字节分页、64 MiB 分区，带无签名 AVB 哈希 footer。脚本为新镜像重新生成 footer，保留 AVB 构建属性并校验哈希；超过分区容量则失败。这不是 OEM 签名，不能绕过已锁定 bootloader 的信任链。

独立的 `dtbo.img` 原样复制，不由此次内核构建生成。若当前系统已经使用该 DTBO，无需仅因 artifact 包含它而重新刷入。

## 刷入前

- **必须解锁 bootloader。** 备份当前 boot 镜像，并确保能够通过 fastboot/recovery 恢复。解锁可能清除数据并影响 Sony DRM 功能。
- 镜像仅适用于匹配的设备和 ROM。内核版本同为 `4.9.337-perf+` 并不保证 vendor 模块或不同 LineageOS 构建兼容；刷入前核对源码版本。
- 设备支持时，先用 `fastboot boot boot.img` 临时启动测试，再考虑永久刷入。不要猜测当前 slot 或盲目刷入双槽，遵循所安装 ROM 的设备专用刷机步骤。
- CI 编译和镜像校验成功，不代表已验证手机能启动或 KernelSU 在设备上正常工作；这些仍需在 H8116 实机确认。

## 来源

- [Sony aurora 设备配置](https://github.com/LineageOS/android_device_sony_aurora/tree/lineage-22.2)
- [Sony tama 公共配置](https://github.com/LineageOS/android_device_sony_tama-common/tree/lineage-22.2)
- [backslashxx KernelSU](https://github.com/backslashxx/KernelSU)
- [AOSP mkbootimg](https://android.googlesource.com/platform/system/tools/mkbootimg/)
- [AOSP AVB](https://android.googlesource.com/platform/external/avb/)
