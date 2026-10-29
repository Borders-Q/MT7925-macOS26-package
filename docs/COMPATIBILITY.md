# 兼容性与实测状态

这里区分组件的匹配范围、上游报告和本仓库的硬件验证。硬件 ID 匹配成功不能直接证明联网、蓝牙音频或睡眠可用。

## 系统构建与模式

| 系统 | Ethernet Wi-Fi 前端 | 原生 Wi-Fi 菜单 | 蓝牙补丁默认状态 |
|---|---|---|---|
| macOS 26.7.1 / `25G241` | 提供；需本机测试 | 上游支持 | LegionBtFix 0.3.0 启用 |
| macOS 26.7.2 / `25G332` | 提供；需本机测试 | 上游支持 | LegionBtFix 0.3.0 启用 |
| 其他 macOS 26 构建 | 作为初始测试模式；不能保证工作 | 上游 ABI 不在允许列表，不启用 | 默认禁用，需独立确认指令匹配 |
| macOS 15 / Darwin 24 | 上游核心曾测试，本包未提供验证过的配置 | 本版本不支持 | 本包配置限定 Darwin 25 |
| Apple Silicon / ARM64 | 不适用 | 不适用 | 本包面向 OpenCore x86_64 |

以上是配置策略和上游适用范围，不是整张表已完成硬件测试。检查构建号使用 `sw_vers -buildVersion`，不要只看“macOS 26”。

## 本仓库目标硬件

| 项目 | 识别信息 | 当前证据 |
|---|---|---|
| 机器 | Alienware 16X Aurora AC16251 | Windows 中识别 |
| Wi-Fi | MediaTek MT7925；PCI `14C3:7925`；子系统 `105B:E123` | 已核对上游 PCI 匹配表 |
| 蓝牙 | USB `0489:E139` | 已核对上游 USB 匹配表 |
| Wi-Fi ACPI 路径 | `PC02.RP06.PXSX` | 已识别；原配置曾存在屏蔽此设备的 SSDT |
| 蓝牙 USB 路径 | `PC02.XHCI.RHUB.HS14` | 原机器 USB 拓扑；不能套用到其他电脑 |
| 新版驱动联网、配对、音频 | 本发布所列版本 | **尚未完成本机实测** |

上游 MtkWlan 还匹配 RZ717 `14C3:0717`；上游原生菜单文档记录另一台 RZ717 机器的 WPA/WPA2 Personal 联网成功报告。本包不扩大该报告的适用范围，也不支持把 MT7921/MT7922 的 ID 填进去冒充 MT7925。

## 验收项目

新报告应注明系统完整构建号、组件版本、PCI/USB ID，并分别报告：

- 固件初始化、扫描、WPA2 关联、DHCP、实际网络访问和持续传输。
- 蓝牙控制器真实地址、BLE 配对、经典蓝牙配对、耳机音频与麦克风。
- 冷启动、暖重启和 Wi-Fi/蓝牙同时工作。

睡眠唤醒、Wi-Fi 6/7、AirDrop/AWDL 不在本包承诺范围内。上游仍有 AirPods 音频断连问题。提交结果请使用 [测试报告模板](https://github.com/Borders-Q/MT7925-macOS26-package/issues/new?template=test-report.yml)。
