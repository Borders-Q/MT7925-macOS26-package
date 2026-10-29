# Changelog

## 0.1.0-alpha.1 — 2026-10-30

- First public-ready integration package; no complete personal EFI is included.
- Pin MtkWlan 0.12.1, MtkWlanNative 0.4.14, MtkBt 0.2.4, LegionBtFix 0.3.0, Lilu 1.7.2 and BlueToolFixup 2.7.2.
- Native build allowlist: 25G241 and 25G332; unknown builds keep the Ethernet profile.
- Include recovery userspace tool source, a cross-compiled client, hidden password entry, DHCP helper and non-destructive config generation.
- Include exact source snapshots, original release archives in the driver bundle, third-party notices, hashes and validation tests.
- Latest source notes replace the earlier package's obsolete statement that there had been no WPA2 on-air report; the new report belongs to an upstream RZ717 tester, not this laptop.
- Package changes only Wi-Fi plist defaults. No guarantee of Wi-Fi/Bluetooth operation on AC16251; runtime validation remains pending.
