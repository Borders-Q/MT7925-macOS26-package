# v0.1.0-alpha.1 — MT7925 macOS 26 integration package

**实验性 Pre-release。** 本整合包的版本号与各上游驱动版本号独立。

整合截至 2026-10-30 的上游最新非预发行版本：MtkWlan 0.12.1、MtkWlanNative 0.4.14、MtkBt 0.2.4、LegionBtFix 0.3.0、Lilu 1.7.2、BlueToolFixup 2.7.2。

目标 ID 为 Wi-Fi `14C3:7925` 与蓝牙 `0489:E139`。原生 Wi-Fi 菜单仅适用于 macOS 构建 `25G241` 和 `25G332`；其他构建先使用 Ethernet 前端。未知构建不默认启用 LegionBtFix。

包含驱动、恢复环境连接工具、配置片段、精确源码快照、许可证与 SHA-256 清单；不包含个人 EFI、SMBIOS、网络凭据或运行日志。

已做资产哈希、ZIP 完整性、硬件 ID 匹配、9 项自动测试、三种方案的 OpenCore 1.0.9 配置校验及用户态客户端静态检查。Alienware AC16251 上的新版本联网、蓝牙配对与音频尚未完成实测；上游仍有 AirPods 断连、睡眠唤醒等限制。CI 和离线检查不代表硬件验证。

下载 `mt7925-macos26-0.1.0-alpha.1.zip`，对照旁边的 `.sha256` 文件校验，并阅读 README 与安装说明。源码 ZIP 是仓库归档，驱动包是独立的 Release 附件。

- [安装说明](https://github.com/Borders-Q/MT7925-macOS26-package/blob/main/docs/INSTALL.zh-CN.md)
- [兼容性与实测状态](https://github.com/Borders-Q/MT7925-macOS26-package/blob/main/docs/COMPATIBILITY.md)
- [完整来源和许可证](https://github.com/Borders-Q/MT7925-macOS26-package/blob/main/NOTICE.md)
