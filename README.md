# KernelSU Boot 镜像构建

**中文** | [English](README_EN.md)

使用 [backslashxx/KernelSU](https://github.com/backslashxx/KernelSU) 构建设备专用 **boot.img** release，不生成 AnyKernel3 刷机包。

- Sony Xperia XZ2 Premium H8116（`aurora`）：LineageOS 22 / Android 15，`4.9.337-perf+`。
- Nothing Phone (1)（`Spacewar`）：Nothing OS 2.0.5 / Android 13，`5.4.210-qgki-gcfce8884187a`。

## 工作流

### Xperia XZ2 Premium H8116

**Build H8116 Kernel** 工作流使用 `h8116-lineage/boot.img`、原样复制的 `h8116-lineage/dtbo.img` 和 `config.env`。它使用 LineageOS `tama_aurora_defconfig` 构建 `Image.gz-dtb`，启用该 fork 的系统调用表 hook，并以 `h8116-<run_number>` 发布结果。

### Nothing Phone (1)

**Build Nothing Phone (1) OS 2.0.5** 工作流使用 `nothing-1-2.0.5/boot.img`、原样复制的 `nothing-1-2.0.5/dtbo.img` 和 `config-nothing-phone-1.env`。它从提供的 boot 镜像提取原厂 QGKI 配置，使用 NothingOSS 发布的 OS 2.0.5 源码构建原始 ARM64 `Image`，并启用 KernelSU ARM64 branch-link 和 LSM hook。

每次 Nothing 构建成功后，自动发布标题为 **Nothing Phone (1) OS 2.0.5** 的 release，包含 `boot.img`、`dtbo.img`、`build-info.txt`、`config.env` 和 `kernel.config`。应安装 [backslashxx/KernelSU releases](https://github.com/backslashxx/KernelSU/releases) 中匹配的 Manager，而非官方 KernelSU Manager。

原厂 Nothing 内核后缀 `gcfce8884187a` 不对应 NothingOSS 公共仓库中的提交。工作流保留要求的 release 字符串，但 `build-info.txt` 记录实际使用的公开源码提交；版本字符串一致不能证明 vendor 模块兼容。

## 镜像处理

`scripts/repack_boot.py` 仅替换内核 payload，保留 ramdisk、boot header 元数据、AVB 属性和其他非内核 payload。它支持提供的 H8116 header-v1 镜像和 Nothing header-v3 镜像，重新生成无签名 AVB 哈希 footer，验证所有保留字段与 payload，并拒绝超过原 boot 分区容量的输出。

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
- [Sony tama 公共配置](https://github.com/LineageOS/android_device_sony_tama-common/tree/lineage-22.2)
- [backslashxx KernelSU](https://github.com/backslashxx/KernelSU)
- [AOSP mkbootimg](https://android.googlesource.com/platform/system/tools/mkbootimg/)
- [AOSP AVB](https://android.googlesource.com/platform/external/avb/)
