#!/bin/bash
# SPDX-License-Identifier: ISC
set -euo pipefail
BASE="$(cd "$(dirname "$0")" && pwd)"
[ "$(uname -s)" = Darwin ] || { echo 'This tool runs in macOS or macOS Recovery.'; exit 1; }
[ "$(id -u)" = 0 ] || { echo 'Use Recovery Terminal, or sudo bash tools/connect-wifi.sh.'; exit 1; }
TMP_DIR="$(mktemp -d /tmp/mt7925-connect.XXXXXX)"
trap 'rm -f "$TMP_DIR/mtkwifi-recovery"; rmdir "$TMP_DIR" 2>/dev/null || true' EXIT
cp "$BASE/bin/mtkwifi-recovery" "$TMP_DIR/mtkwifi-recovery"
chmod 700 "$TMP_DIR/mtkwifi-recovery"
CLIENT="$TMP_DIR/mtkwifi-recovery"
"$CLIENT" --selftest
sw_vers
STATUS="$("$CLIENT" status)"
printf '%s\n' "$STATUS"
if printf '%s\n' "$STATUS" | grep -q 'frontend=1'; then
  echo 'Native Wi-Fi is active. Select your network in the macOS Wi-Fi menu.'
  exit 0
fi
"$CLIENT" scan
printf 'Wi-Fi SSID (exact name): '
IFS= read -r SSID
[ -n "$SSID" ] || { echo 'No SSID entered.'; exit 1; }
"$CLIENT" join "$SSID"
INTERFACES="$(ioreg -r -c MtkWlan -l -w0 | sed -n 's/.*"BSD Name" = "\(en[0-9][0-9]*\)".*/\1/p' | sort -u)"
if [ -z "$INTERFACES" ] || [ "$(printf '%s\n' "$INTERFACES" | wc -l | tr -d ' ')" != 1 ]; then
  echo 'Associated, but a unique MtkWlan interface was not found. Check ioreg before requesting DHCP.'
  exit 2
fi
ipconfig set "$INTERFACES" DHCP
COUNT=0
while [ "$COUNT" -lt 20 ]; do
  ADDRESS="$(ipconfig getifaddr "$INTERFACES" 2>/dev/null || true)"
  if [ -n "$ADDRESS" ]; then
    echo "DHCP address: $ADDRESS. Check access in the installer or browser."
    exit 0
  fi
  COUNT=$((COUNT + 1))
  sleep 1
done
echo 'Associated, but no DHCP address was received within 20 seconds.'
exit 3
