# Validation scope

The package pins upstream releases checked on 2026-10-30. Release-asset SHA-256 values come from the GitHub release API and are verified before extracting. ZIP CRC, source snapshot hashes, kernel Mach-O architecture/type and declared versions are checked during assembly. Kernel executables remain unchanged; final files are recorded in SHA256SUMS.

Python tests cover preserving unrelated OpenCore settings, exact native-build gating, dependency order, idempotent merging, explicitly requested board masking changes, competing drivers, archive path traversal, executable permissions and source snapshot integrity. The recovery client has compile-time ABI size assertions and an IEEE WPA2 PMK known-answer test. Independent host PMK comparisons and Mach-O signature page-hash checks were performed locally; recorded results are included in the publication validation report outside the repository.

The first [GitHub Actions validation run](https://github.com/Borders-Q/MT7925-macOS26-package/actions/runs/40970842966) passed on 2026-10-30 (Asia/Shanghai). The Ubuntu job passed all 9 Python tests, shell syntax and bundled-client signature page checks. The Intel macOS job rebuilt the userspace client, ran its WPA2 PMK self-test and passed strict codesign verification. These results validate the userspace source build and automated checks; they do not exercise the bundled cross-compiled executable, PCI/USB hardware or a Wi-Fi connection.

No current release has been booted by this packaging session on the target Alienware AC16251. Missing acceptance evidence includes firmware attach, WPA2 association, DHCP and internet traffic, Bluetooth controller adoption, BLE pairing, audio and restart behavior. The prior personal EFI was deployed with older components; that is not evidence that these releases work on this laptop.

Upstream reports are attributed in README and source snapshots. The Wi-Fi core tag README still has an older WPA2-unverified paragraph, while the newer native front-end README records an external RZ717 success report. The package documents this distinction instead of silently treating every upstream claim as a local result.
