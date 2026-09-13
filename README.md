# KernelSU Boot 镜像构建

**中文** | [English](README_EN.md)

使用 [backslashxx/KernelSU](https://github.com/backslashxx/KernelSU) 构建设备专用 **boot.img** release，不生成 AnyKernel3 刷机包。

- Sony Xperia XZ2 Premium H8116（`aurora`）：LineageOS 22 / Android 15，`4.9.337-perf+`。
- Nothing Phone (1)（`Spacewar`）：Nothing OS 2.0.5 / Android 13，`5.4.210-qgki-gcfce8884187a`。
- Nothing Phone (1)（`Spacewar`）：Nothing OS 3.2（Spacewar-V3.2-260206-1016），`5.4.289-qgki-g49c0dcb3dc63`。

## 工作流

### Xperia XZ2 Premium H8116

**Build H8116 Kernel** 工作流使用 `h8116-lineage/boot.img`、原样复制的 `h8116-lineage/dtbo.img` 和 `config.env`。它使用 LineageOS `tama_aurora_defconfig` 构建 `Image.gz-dtb`，启用该 fork 的系统调用表 hook，并以 `h8116-<run_number>` 发布结果。

### Nothing Phone (1)

**Build Nothing Phone (1) OS 2.0.5** 工作流使用 `nothing-1-2.0.5/boot.img`、原样复制的 `nothing-1-2.0.5/dtbo.img` 和 `config-nothing-phone-1.env`。它从提供的 boot 镜像提取原厂 QGKI 配置，使用 NothingOSS 发布的 OS 2.0.5 源码构建原始 ARM64 `Image`，并启用 KernelSU ARM64 branch-link 和 LSM hook。

### Nothing Phone (1) — Nothing OS 3.2

**Build Nothing Phone (1) OS 3.2** 工作流使用 `nothing-1-3.2-260206/boot.img`、原样复制的 `nothing-1-3.2-260206/dtbo.img` 和 `config-nothing-phone-1-os32.env`。它使用 `sm7325/v/mr` 分支上固定到 OS 3.2 `Spacewar-V3.2-260206-1016` 合并提交的源码构建原始 ARM64 `Image`，采用与 OS 2.0.5 工作流相同的原厂配置提取和 KernelSU hook。

每次 Nothing 构建成功后，自动发布标题为 **Nothing Phone (1) OS 2.0.5** 或 **Nothing Phone (1) OS 3.2** 的 release，包含 `boot.img`、`dtbo.img`、`build-info.txt`、`config.env` 和 `kernel.config`。应安装 [backslashxx/KernelSU releases](https://github.com/backslashxx/KernelSU/releases) 中匹配的 Manager，而非官方 KernelSU Manager。

原厂 Nothing 内核后缀 `gcfce8884187a` 和 `g49c0dcb3dc63` 均不对应 NothingOSS 公共仓库中的提交。工作流保留要求的 release 字符串，但 `build-info.txt` 记录实际使用的公开源码提交；版本字符串一致不能证明 vendor 模块兼容。

## KernelSU 与 Manager 兼容性

内核基于 [backslashxx/KernelSU](https://github.com/backslashxx/KernelSU) 的 **v3.3.0-28** release tag 构建，其内核报告的 UAPI 版本为 **4**。

Manager 会比较自身与内核的 UAPI 版本，只要内核更低就会显示 **"Kernel update required"**，与 app 版本号无关。请安装匹配的 **v3.3.0-28** Manager APK（`KernelSU_v3.3.0-28_32629-release.apk`）；如需使用更新的 Manager，必须先用 UAPI 版本相同或更高的 KernelSU 修订重新构建内核。

使用更旧 KernelSU 修订构建的内核报告 UAPI v3，会始终显示该提示：过时的是内核而不是 app。每个工作流都会校验所固定修订的 `kernel/include/uapi/supercall.h` 是否报告预期 UAPI 版本，不符则构建失败。

## 镜像处理

`scripts/repack_boot.py` 仅替换内核 payload，保留 ramdisk、boot header 元数据、AVB 属性和其他非内核 payload。它支持提供的 H8116 header-v1 镜像和两个 Nothing header-v3 镜像，重新生成无签名 AVB 哈希 footer，验证所有保留字段与 payload，并拒绝超过原 boot 分区容量的输出。

独立的 `dtbo.img` 会被复制并校验为完全不变；它不由任何内核构建生成。不要仅因 release 中包含它而刷入。

这不是 OEM 签名，不能使自定义镜像通过已锁定 bootloader 的信任链。

## 刷入前

- **必须解锁 bootloader。** 备份当前 boot 镜像，并确认设备专用的恢复方法。
- 镜像仅适用于匹配的设备和 ROM。内核 release 字符串一致不能证明与已安装 vendor 模块兼容。
- 设备支持时，先用 `fastboot boot boot.img` 临时启动测试。不要猜测当前 slot 或盲目刷入双槽。
- CI 编译和镜像校验成功，不代表手机一定能启动或 KernelSU 能在实机正常工作。

## 来源

- [Sony aurora 设备配置](https://github.com/LineageOS/android_device_sony_aurora/tree/lineage-22.2)
- [NothingOSS Phone (1) 内核](https://github.com/NothingOSS/android_kernel_msm-5.4_nothing_sm7325/tree/sm7325/t)
- [NothingOSS Phone (1) 内核（OS 3.x MR 分支）](https://github.com/NothingOSS/android_kernel_msm-5.4_nothing_sm7325/tree/sm7325/v/mr)
- [Sony tama 公共配置](https://github.com/LineageOS/android_device_sony_tama-common/tree/lineage-22.2)
- [backslashxx KernelSU](https://github.com/backslashxx/KernelSU)
- [AOSP mkbootimg](https://android.googlesource.com/platform/system/tools/mkbootimg/)
- [AOSP AVB](https://android.googlesource.com/platform/external/avb/)
