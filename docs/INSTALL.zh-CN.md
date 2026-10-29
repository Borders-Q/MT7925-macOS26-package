# 安装与回退

本包仅包含无线网卡相关组件。需要一套已经能启动目标 macOS 的 OpenCore EFI；先保存可启动的原版 EFI。安装修改的是引导配置，不是 Windows 网卡驱动或设备闪存。

## 1. 确认构建号与硬件

在 macOS 或恢复环境终端运行 `sw_vers`。原生菜单仅支持 `25G241`、`25G332`。未知构建使用 Ethernet 前端，不删除上游的 ABI 检查。

目标设备是 PCI `14C3:7925` 和 USB `0489:E139`；上游还匹配其他 MT7925 ID，这不代表已在本项目中逐一测试。MT7921/MT7922 不能仅改 ID 后使用本包。

## 2. 复制驱动并合并配置

将发布包 `Kexts/` 中需要的 kext 复制到已有 EFI 的 `OC/Kexts/`。已有相同 kext 时先保留原文件并检查版本；Lilu 需 1.7.2 或经验证的更新版本，不要用本包降级替换现有版本。

加载顺序：`Lilu → BlueToolFixup → LegionBtFix（可选）→ MtkBt → MtkWlan → MtkWlanNative（可选）`。MtkWlan、MtkBt 本身不依赖 Lilu；BlueToolFixup 和 LegionBtFix 需要它。

可以手工合并 examples 的片段，也可用 Python 生成**新的配置副本**：

```bash
# 在能运行 Python 的系统中执行；不会更改输入文件，也不会复制或加载 kext。
python3 scripts/configure.py /path/to/config.plist /path/to/config-mt7925.plist --mode ethernet

# 已确认构建号时启用原生菜单和已知适用的蓝牙补丁：
python3 scripts/configure.py /path/to/config.plist /path/to/config-mt7925.plist --mode native --build 25G332
```

片段与脚本约束为 Darwin `25.0.0` 到 `25.99.99`。构建号未知时 LegionBtFix 默认禁用；它的 0.3.0 虽不再硬编码一个版本，仍需要实际匹配系统的 bluetoothd 指令。对照上游文档和日志决定是否在其他构建启用。

脚本保留无关配置与已有 Lilu 项，将其放到插件之前，避免重复添加。存在竞争的 MT7925 驱动时会停止。复制与配置审阅完成后，用**与你 OpenCore 相同版本**的 ocvalidate 检查，再通过备份启动盘测试。

## 3. 蓝牙 NVRAM 与 USB

在 `NVRAM > Add > 7C436110-AB2A-4BBB-A880-FE41995C9F82` 中添加：

| 键 | 类型 | 值 |
|---|---|---|
| bluetoothExternalDongleFailed | Data | `00` |
| bluetoothInternalControllerInfo | Data | **14 个零字节**，即 `0000000000000000000000000000` |

两项也应列入同 GUID 的 `NVRAM > Delete`，使引导时替换旧值。原生模式追加 `mtkfe=native mtknativeif=1` 到现有 boot-args，并把 `boot-args` 列入 Delete；保留原有必要参数。配置辅助脚本已处理这些项目。

USB 映射必须包括蓝牙的实际内部端口。AC16251 初次识别为 `PC02.XHCI.RHUB.HS14`、内部接口 `255`；其他电脑不能直接套用端口编号。本包不提供通用 USB 映射。

## 4. AC16251 的已知 Wi-Fi 屏蔽项

最初目标 EFI 含有 `SSDT-Disable_Network_RP06.aml`，会向 `PC02.RP06.PXSX` 注入无效设备/厂商/类别值，阻止 MT7925 匹配。该机器的 Wi-Fi 位置已在 Windows 中识别为此路径。

只有在你确认自己的机器和表相同后，才停用这一项。配置脚本通过 `--unmask-rp06` 显式处理；默认不改 ACPI。不要把此选项当成所有 MT7925 电脑的必要步骤。

## 5. 恢复环境联网与验证

Ethernet 模式使用 `tools/connect-wifi.sh`，密码在终端隐藏输入。工具内置 IEEE WPA2 PMK 自检，连接后申请 DHCP。它只在本次进程中使用派生密钥；不要在公开 kext 的 `MtkAutoNetworks` 中写入自己家的 PMK。

原生模式使用系统 Wi-Fi 菜单。若没有菜单，先查 `ioreg -r -c MtkWlanNative -l -w0` 的 ABI 和接口状态；构建不匹配时退回 Ethernet 模式。

```bash
kmutil showloaded | grep -E 'MtkWlan|MtkBt|Lilu|BlueToolFixup|LegionBtFix'
ioreg -r -c MtkWlan -l -w0
ioreg -r -c MtkBt -l -w0
system_profiler SPBluetoothDataType
```

蓝牙应出现真实控制器地址与 On 状态，固件加载器应报告 `MtkBtState=ready`。仅恢复环境中的识别不等同于桌面配对、BLE 和音频验证。上游 AirPods 断连问题尚未解决；需要进一步检查共存和音频链路。

测试冷启动、暖重启、WPA2 关联、DHCP、实际网络访问、蓝牙配对与音频。日志可能包含 SSID、MAC 和机器信息；在发到 GitHub 前自行脱敏。本包不自动采集或上传日志，也不自动打开 HCI 音频记录。

## 回退

通过原启动盘进入系统，将原 `config.plist` 与旧驱动恢复；或禁用新增驱动项。若使用过本包添加的蓝牙 NVRAM 项，按原备份恢复该配置。不要用别人的完整 EFI 覆盖整机配置。
