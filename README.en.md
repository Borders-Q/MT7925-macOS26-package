# MT7925 macOS 26 package

[![Validate package](https://github.com/Borders-Q/MT7925-macOS26-package/actions/workflows/validate.yml/badge.svg)](https://github.com/Borders-Q/MT7925-macOS26-package/actions/workflows/validate.yml)

[中文](README.md) · [Download pre-release](https://github.com/Borders-Q/MT7925-macOS26-package/releases/tag/v0.1.0-alpha.1) · [Compatibility](docs/COMPATIBILITY.md) · [Report an issue](https://github.com/Borders-Q/MT7925-macOS26-package/issues/new/choose)

An experimental OpenCore integration package for MT7925 Wi-Fi and Bluetooth, with a recovery-environment userspace client. Package version: **0.1.0-alpha.1**. Kernel drivers are upstream projects credited in [NOTICE.md](NOTICE.md).

Checked against GitHub latest non-prerelease releases on **2026-10-30**: MtkWlan **0.12.1**, MtkWlanNative **0.4.14**, MtkBt **0.2.4**, LegionBtFix **0.3.0**, Lilu **1.7.2**, BlueToolFixup **2.7.2**. Exact commits and asset hashes are in [dependencies.lock.json](dependencies.lock.json).

Target: Intel x86_64 macOS 26, MT7925 PCI `14C3:7925`, Bluetooth USB `0489:E139`. The original target laptop is Alienware AC16251; successful Wi-Fi, pairing and audio operation on that laptop has **not been confirmed**. Keep releases marked **Pre-release** until validated.

MtkWlanNative 0.4.14 supports only **25G241** (26.7.1) and **25G332** (26.7.2). Other builds use the Ethernet front end. LegionBtFix 0.3.0 uses masked byte windows and is tested upstream on those two builds; the helper leaves it disabled on unknown builds. The native upstream documentation reports a WPA/WPA2 Personal join on another RZ717 system; that is not this laptop's validation.

## Install

Download `mt7925-macos26-0.1.0-alpha.1.zip` and its `.sha256` from [Releases](https://github.com/Borders-Q/MT7925-macOS26-package/releases/tag/v0.1.0-alpha.1). The driver release ZIP contains `Kexts/`, tools, example fragments, licenses and source snapshots. GitHub's **Source code (zip)** is the packaging repository, not a ready-to-install driver bundle. Verify the download with `shasum -a 256` or PowerShell `Get-FileHash -Algorithm SHA256`. After extraction, `shasum -a 256 -c SHA256SUMS` checks individual files.

Keep a bootable backup EFI and merge the examples into an existing OpenCore configuration. The examples are **fragments, not complete boot configurations**. Keep an existing compatible newer Lilu rather than downgrading it.

See [the installation guide](docs/INSTALL.zh-CN.md) for load order, NVRAM data, USB mapping and recovery. `scripts/configure.py` creates a separate config copy and refuses to overwrite existing files. It never copies drivers or changes an active EFI.

On a supported native build, use the macOS Wi-Fi menu. Otherwise run in Recovery Terminal:

```bash
bash /Volumes/<volume>/mt7925-macos26-0.1.0-alpha.1/tools/connect-wifi.sh
```

Enter an SSID and WPA2 password at the hidden prompt. No password or PMK is persisted. The script requests DHCP only on the uniquely identified MtkWlan interface; an IP address is not proof of internet access.

## Build

Requires Python 3.10+ and curl. To rebuild the userspace client, use macOS Command Line Tools or LLVM with clang and ld64.lld. A cross-compiled x86_64 client is supplied; execution on the target Mac remains unverified.

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_recovery.py
python3 scripts/build_release.py
python3 scripts/check_latest.py
```

For cross-compilation: `python scripts/build_recovery.py --llvm-bin <LLVM-bin>`. Release assembly verifies pinned asset hashes, preserves upstream kernel binaries, includes corresponding source snapshots and writes a file hash manifest. CI has been prepared; no CI success is claimed before GitHub runs it.

## Limits and changes

No 802.11ax/be, AWDL/AirDrop/Continuity, reliable sleep/wake, WPA3-only, required-PMF or enterprise authentication. Bluetooth recognition, BLE and audio need separate validation. Upstream still reports AirPods dropouts; audio-payload HCI logging is not enabled by this package. LegionBtFix's LE workaround uses the public controller address and changes LE privacy behavior.

Only the MtkWlan plist is adjusted: empty auto-open/auto-network arrays, Ethernet default, and `MtkPower=false` to retain the earlier integration's firmware-default power strategy. Kernel executables remain unchanged. This power setting may reduce performance.

Personal EFI, SMBIOS identifiers, network credentials and runtime logs are excluded. Packaging/helper code uses ISC; third-party code and firmware retain their own licenses. GPL source snapshots and build scripts travel with the release. See [NOTICE.md](NOTICE.md).

Maintained by [Borders-Q](https://github.com/Borders-Q). See [CONTRIBUTING.md](CONTRIBUTING.md) for test reports and dependency updates.
