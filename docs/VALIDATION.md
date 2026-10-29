# Validation scope

The package pins upstream releases checked on 2026-10-30. Release-asset SHA-256 values come from the GitHub release API and are verified before extracting. ZIP CRC, source snapshot hashes, kernel Mach-O architecture/type and declared versions are checked during assembly. Kernel executables remain unchanged; final files are recorded in SHA256SUMS.

Python tests cover preserving unrelated OpenCore settings, exact native-build gating, dependency order, idempotent merging, explicitly requested board masking changes, competing drivers, archive path traversal, executable permissions and source snapshot integrity. The recovery client has compile-time ABI size assertions and an IEEE WPA2 PMK known-answer test. Independent host PMK comparisons and Mach-O signature page-hash checks were performed locally; recorded results are included in the publication validation report outside the repository.

The GitHub Actions workflow has been authored but not run in a hosted GitHub repository. It builds and self-tests the client on an Intel macOS runner; a future green result would validate the userspace build, not the PCI/USB hardware.

No current release has been booted by this packaging session on the target Alienware AC16251. Missing acceptance evidence includes firmware attach, WPA2 association, DHCP and internet traffic, Bluetooth controller adoption, BLE pairing, audio and restart behavior. The prior personal EFI was deployed with older components; that is not evidence that these releases work on this laptop.

Upstream reports are attributed in README and source snapshots. The Wi-Fi core tag README still has an older WPA2-unverified paragraph, while the newer native front-end README records an external RZ717 success report. The package documents this distinction instead of silently treating every upstream claim as a local result.
