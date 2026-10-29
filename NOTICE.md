# Third-party attribution and source distribution

This is an integration and packaging project. Kernel driver authors retain all credits and rights. The packaging version is independent of upstream driver versions. No upstream author is represented as endorsing this package.

| Component | Upstream | License |
|---|---|---|
| MtkWlan | watchthelight-labs/mt7925-hackintosh-wifi | ISC; Clear BSD adapted parts; MediaTek firmware terms |
| MtkWlanNative | watchthelight-labs/mt7925-hackintosh-wifi-native | ISC; Clear BSD adapted parts |
| MtkBt | watchthelight-labs/mt7925-hackintosh-bluetooth | ISC; Clear BSD adapted parts; MediaTek firmware terms |
| LegionBtFix | watchthelight-labs/LegionBtFix | GPL-2.0; adapted from BlueToolFixup; Lilu support code has BSD terms |
| Lilu | acidanthera/Lilu | BSD-3-Clause; bundled disassembler components retain their licenses |
| BlueToolFixup | acidanthera/BrcmPatchRAM, created by Dhinak G | GPL-2.0 |
| MtkCrypto.c/.h in tools/vendor | MtkWlan; adapted from thanhnndev and contributors' itlmt7925 | BSD-3-Clause-Clear; full notices remain in the files |
| MtkUserApi.h in tools/vendor | MtkWlan / watchthelight | ISC |

Upstream also credits Linux mt76/btmtk, MediaTek, Felix Fietkau and contributors, thanhnndev and contributors, OpenIntelWireless and others. Original LICENSE, NOTICE and LICENSES files are preserved in `licenses/` and source snapshots. Consult those notices for file-level terms and history.

`dependencies.lock.json` records the exact upstream source commit and release asset SHA-256. `third_party/sources/` carries the complete Git-tracked source trees and build scripts at those pinned commits, including the GPL components, rather than a link-only source offer. Generated and ignored build products and the `.git` databases are excluded. No claim is made that third-party binaries were reproduced by this packaging project. Full Lilu source is also included for the LegionBtFix build. Standard OS/compiler tooling remains a build prerequisite; some upstream build scripts fetch their own documented SDK/toolchain dependencies.

For BlueToolFixup, only its kext is installed; the original BrcmPatchRAM release archive is retained for provenance. MediaTek firmware is embedded as in upstream MtkWlan/MtkBt and remains subject to `LICENCE.mediatek`. No Windows driver, Apple kernel collection or macOS system library is included.

Changes to upstream artifacts are limited to the packaged MtkWlan Info.plist: empty `MtkAutoOpenSsids` and `MtkAutoNetworks`, and `MtkPower=false`. All kernel executables remain byte-for-byte upstream. Source snapshots are unmodified. The recovery client is new userspace glue and uses the pinned public IOUserClient ABI and unmodified upstream crypto sources.

The root ISC LICENSE covers original packaging scripts, documentation and the userspace glue. It does not relicense upstream material. Any future changes should retain this attribution and distribute corresponding source with GPL binaries.
