# MT7925 macOS 26 驱动整合包

[![Validate package](https://github.com/Borders-Q/MT7925-macOS26-package/actions/workflows/validate.yml/badge.svg)](https://github.com/Borders-Q/MT7925-macOS26-package/actions/workflows/validate.yml)

[English](README.en.md) · [下载预发布包](https://github.com/Borders-Q/MT7925-macOS26-package/releases/tag/v0.1.0-alpha.1) · [安装说明](docs/INSTALL.zh-CN.md) · [兼容性](docs/COMPATIBILITY.md) · [报告问题](https://github.com/Borders-Q/MT7925-macOS26-package/issues/new/choose)

面向 MediaTek MT7925 的 OpenCore Wi-Fi / 蓝牙驱动整合、恢复环境联网工具和安装示例。包装版本为 **0.1.0-alpha.1**。

本项目整合既有开源内核驱动，并提供配置辅助脚本与用户态联网工具。内核驱动作者是下列上游项目；本项目不声称独立开发了这些驱动。

**状态：实验性预发布。** 已完成下载校验、硬件 ID 匹配及离线配置检查；尚未取得 Alienware AC16251 上新版本的 macOS 联网、蓝牙配对或音频实测结果。CI 检查和上游报告都不代表本机硬件验收通过。

## 版本与来源

截至 **2026-10-30**，通过 GitHub `/releases/latest` 检查到的最新非预发行版本：

| 组件 | 锁定版本 | 来源 |
|---|---|---|
| MtkWlan，Wi-Fi 核心 | 0.12.1 | [watchthelight-labs/mt7925-hackintosh-wifi](https://github.com/watchthelight-labs/mt7925-hackintosh-wifi/releases/tag/0.12.1) |
| MtkWlanNative，原生 Wi-Fi 菜单 | 0.4.14 | [watchthelight-labs/mt7925-hackintosh-wifi-native](https://github.com/watchthelight-labs/mt7925-hackintosh-wifi-native/releases/tag/0.4.14) |
| MtkBt，蓝牙固件加载 | 0.2.4 | [watchthelight-labs/mt7925-hackintosh-bluetooth](https://github.com/watchthelight-labs/mt7925-hackintosh-bluetooth/releases/tag/0.2.4) |
| LegionBtFix，蓝牙用户态兼容补丁 | 0.3.0 | [watchthelight-labs/LegionBtFix](https://github.com/watchthelight-labs/LegionBtFix/releases/tag/0.3.0) |
| Lilu | 1.7.2 | [acidanthera/Lilu](https://github.com/acidanthera/Lilu/releases/tag/1.7.2) |
| BlueToolFixup | 2.7.2 | [acidanthera/BrcmPatchRAM](https://github.com/acidanthera/BrcmPatchRAM/releases/tag/2.7.2) |

精确提交、下载 URL 和 SHA-256 见 [dependencies.lock.json](dependencies.lock.json)。`latest` 是上游的发布标记，不等同于所有机器均稳定可用；本包不追踪未发布的开发版。

## 硬件与系统

- 目标 Wi-Fi：MT7925，PCI `14C3:7925`。最初适配机器为 Alienware 16X Aurora AC16251，子系统 `105B:E123`。
- 目标蓝牙：同一卡的 USB 设备 `0489:E139`；已核对 MtkBt 的匹配表包含此 ID。
- 目标系统：Intel x86_64 macOS 26 / Darwin 25，通过 OpenCore 注入。
- **原生菜单严格限定 `25G241`（26.7.1）与 `25G332`（26.7.2）。** 请运行 `sw_vers -buildVersion` 核对。其他构建号先使用 Ethernet 前端；本包不解除上游 ABI 限制。
- LegionBtFix 0.3.0 采用字节窗口匹配，上游实测为上述两个构建号。配置辅助脚本仅在这两个构建号上默认启用它；未知构建上的蓝牙配对兼容性仍需验证。

上游 MtkWlanNative 0.4.14 文档已记录另一台 RZ717 机器通过 WPA/WPA2 Personal 连接、DHCP 和自动重连的报告。这不构成本项目目标机器的实测结果。

## 使用发布包

从 [Releases](https://github.com/Borders-Q/MT7925-macOS26-package/releases/tag/v0.1.0-alpha.1) 下载 `mt7925-macos26-0.1.0-alpha.1.zip` 及旁边的 `.sha256`。包内有 `Kexts/`、`tools/`、示例配置、许可证、完整上游源码快照和 `SHA256SUMS`。GitHub 的 **Source code (zip)** 是打包仓库源码，不是即用驱动包。

校验整个下载包：macOS 使用 `shasum -a 256 文件.zip`；Windows PowerShell 使用 `Get-FileHash .\文件.zip -Algorithm SHA256`，与 `.sha256` 中的值对照。解压后，macOS 可运行 `shasum -a 256 -c SHA256SUMS` 检查包内文件。

1. 保留一份可启动的原 EFI；将发布包中的相关 kext 复制到已有的 `EFI/OC/Kexts/`。
2. 按 [安装说明](docs/INSTALL.zh-CN.md) 合并 `Kernel > Add` 和蓝牙 NVRAM 项。**examples 中的 plist 只是片段，不能代替完整的 config.plist。**
3. 已有 Lilu 时保留经验证可用的相同或更新版本，不要用本包的 1.7.2 降级替换；本包不带整机 EFI、SMBIOS 或 USB 映射。
4. 原生模式在支持的构建上使用 Wi-Fi 菜单；其他情况下，在恢复环境终端运行：

   ```bash
   bash /Volumes/<卷名>/mt7925-macos26-0.1.0-alpha.1/tools/connect-wifi.sh
   ```

   输入网络名称和隐藏输入的 WPA2 密码。工具不保存密码或 PMK；关联成功后，只为 MtkWlan 对应接口申请 DHCP。得到 IP 还需在安装器或浏览器验证外网访问。

## 从源码组装发布包

需要 Python 3.10+、curl；重建客户端需要 macOS Command Line Tools，或带 `clang` 和 `ld64.lld` 的 LLVM。

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_recovery.py               # 在 macOS 重建用户态工具
python3 scripts/build_release.py                # 下载锁定资产、验哈希、生成 dist/ 发布包
python3 scripts/check_latest.py                 # 仅检查新版本，不自动更改锁定版本
```

仓库随附已交叉编译的 `tools/bin/mtkwifi-recovery`，Windows 上组装发布包可直接使用；其 macOS 实际运行仍待验证。交叉编译可运行 `python scripts/build_recovery.py --llvm-bin <LLVM-bin>`。这只编译用户态工具，内核驱动使用上游发布二进制。

## 已知边界

- 使用 802.11n/ac；不提供硬件完整的 Wi-Fi 7 功能、AirDrop/AWDL/Continuity 或可靠睡眠唤醒。
- WPA3-only、802.1X 企业认证与强制 PMF 网络不受当前驱动支持；请使用有权访问的 WPA2-Personal/AES 网络。
- 蓝牙识别、BLE 配对与音频分别验证；上游仍记录 AirPods 音频断连问题。本包不自动启用会记录音频负载的 HCI 跟踪变通方案。
- LegionBtFix 的 LE 修复会使用公开控制器地址，改变 LE 地址隐私行为；详见随附上游文档。
- MtkWlan 的内核二进制保持上游原样；仅清空 `MtkAutoOpenSsids` 和 `MtkAutoNetworks`，并将 `MtkPower` 设为 `false`，保持此前适配使用的固件默认功率策略。该设置可能影响性能。

## 归属与隐私

[NOTICE.md](NOTICE.md) 列出组件来源和许可证。整合脚本与用户态工具采用 ISC；内核驱动、第三方密码学代码和固件保留各自许可证。GPL 组件的对应标签源码及构建脚本随 `third_party/sources/` 一同分发。

本仓库不含个人完整 EFI、序列号、MLB/ROM、Wi-Fi 凭据、运行日志或本机部署脚本。提交问题时请说明系统构建号与硬件 ID，并自行脱敏日志。

项目维护：[Borders-Q](https://github.com/Borders-Q)。参与测试、更新锁定依赖或提交修复前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。
