# 参与测试与维护

本项目维护 MT7925 相关上游驱动的版本锁定、发布包、用户态工具和配置说明。内核驱动代码的原作者与许可证见 [NOTICE.md](NOTICE.md)。

## 提交测试结果

使用 [测试报告](https://github.com/Borders-Q/MT7925-macOS26-package/issues/new?template=test-report.yml)，注明 `sw_vers` 的完整输出、机器型号、PCI/USB ID、驱动版本以及前端模式。分别说明 Wi-Fi、蓝牙识别、配对和音频结果；不要将“配置校验通过”写成“硬件可用”。

请在自己的电脑上检查日志再粘贴相关片段。日志应移除序列号、MLB/ROM、设备地址、网络名称、IP、个人路径、密码和 PMK。不要上传完整 EFI 或注入了凭据的 kext。项目不会要求提供 GitHub 密码或访问令牌。

## 提交打包或工具修复

```bash
python3 -m unittest discover -s tests -v
bash -n tools/connect-wifi.sh
python3 scripts/verify_client.py
```

改变用户态客户端时，还应在 Intel macOS 上运行 `python3 scripts/build_recovery.py`、`tools/bin/mtkwifi-recovery --selftest` 和 `codesign --verify --strict tools/bin/mtkwifi-recovery`。这些检查不需要加载内核驱动，也不能替代硬件测试。

配置修改要保留原有设置，使用新文件输出，避免写入正在使用的 EFI。原生模式必须保持精确构建允许列表。面向特定机器的 ACPI 修改需要显式选项和解释，不能变成所有机器的默认值。

## 更新依赖

1. 运行 `python3 scripts/check_latest.py`，阅读上游 Release、变更记录及当前已知限制。
2. 核对下载资产的 SHA-256、标签指向的提交和许可证；更新 `dependencies.lock.json`。
3. 更新 `third_party/sources/` 的完整对应源码快照和源码哈希。GPL 二进制必须连同相应源码与构建脚本分发。
4. 如 IOUserClient ABI 或密码学代码发生变化，更新 `tools/vendor/` 并重建工具；核对结构布局、自检和独立密码学测试。
5. 更新 README、兼容性、CHANGELOG 和发布说明，然后重新生成 Release ZIP、SHA256SUMS 与 ZIP 校验值。

发布版本号属于本整合包，不能冒用为某个上游驱动的新版本。除非有具体硬件实测证据，新整合版本应作为 Pre-release 发布。
