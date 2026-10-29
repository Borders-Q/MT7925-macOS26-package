#!/usr/bin/env python3
"""Write a new OpenCore config copy, preserving unrelated settings. Does not install."""
import argparse
import copy
from pathlib import Path
import plistlib

GUID = '7C436110-AB2A-4BBB-A880-FE41995C9F82'
NATIVE_BUILDS = {'25G241', '25G332'}
ORDER = ['Lilu', 'BlueToolFixup', 'LegionBtFix', 'MtkBt', 'MtkWlan', 'MtkWlanNative']


def kext_entry(name, enabled=True):
    return {'Arch': 'x86_64', 'BundlePath': name+'.kext',
            'Comment': 'MT7925 package; see compatibility documentation', 'Enabled': enabled,
            'ExecutablePath': 'Contents/MacOS/'+name, 'PlistPath': 'Contents/Info.plist',
            'MinKernel': '25.0.0', 'MaxKernel': '25.99.99'}


def configure(original, mode='ethernet', build='', unmask_rp06=False):
    if mode not in ('ethernet', 'native'):
        raise ValueError('Unknown mode')
    if mode == 'native' and build not in NATIVE_BUILDS:
        raise ValueError('Native Wi-Fi requires an exact supported build: 25G241 or 25G332')
    config = copy.deepcopy(original)
    entries = config.setdefault('Kernel', {}).setdefault('Add', [])
    conflicts = ('itlmt7925', 'simplemtkwlan', 'airportmtkwlan', 'mtkbtfw', 'simplemtkbtfw')
    for entry in entries:
        if entry.get('Enabled') and any(c in entry.get('BundlePath', '').lower() for c in conflicts):
            raise ValueError('Disable the existing competing MT7925 driver before preparing this profile')
    lilu = next((copy.deepcopy(e) for e in entries if e.get('BundlePath') == 'Lilu.kext'), None)
    entries[:] = [e for e in entries if e.get('BundlePath') not in {x+'.kext' for x in ORDER}]
    new = []
    for name in ORDER:
        enabled = (name != 'MtkWlanNative' or mode == 'native') and (name != 'LegionBtFix' or build in NATIVE_BUILDS)
        if name == 'Lilu' and lilu:
            lilu['Enabled'] = True
            new.append(lilu)
        else:
            new.append(kext_entry(name, enabled))
    # Lilu must precede existing plugins as well as the newly added ones.
    entries[:0] = new
    nvram = config.setdefault('NVRAM', {})
    add = nvram.setdefault('Add', {}).setdefault(GUID, {})
    tokens = add.get('boot-args', '').split()
    tokens = [t for t in tokens if not t.startswith(('mtkfe=', 'mtknativeif='))]
    if mode == 'native':
        tokens += ['mtkfe=native', 'mtknativeif=1']
    add['boot-args'] = ' '.join(tokens)
    add['bluetoothExternalDongleFailed'] = b'\0'
    add['bluetoothInternalControllerInfo'] = b'\0'*14
    delete = nvram.setdefault('Delete', {}).setdefault(GUID, [])
    for key in ('boot-args', 'bluetoothExternalDongleFailed', 'bluetoothInternalControllerInfo'):
        if key not in delete:
            delete.append(key)
    if unmask_rp06:
        matches = [e for e in config.get('ACPI', {}).get('Add', [])
                   if e.get('Path') == 'SSDT-Disable_Network_RP06.aml']
        if not matches:
            raise ValueError('The named RP06 masking SSDT is absent; no ACPI entry was changed')
        for entry in matches:
            entry['Enabled'] = False
    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--mode', choices=['ethernet', 'native'], default='ethernet')
    parser.add_argument('--build', default='', help='Actual output of sw_vers -buildVersion')
    parser.add_argument('--unmask-rp06', action='store_true', help='Only for the documented AC16251 masking SSDT')
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        parser.error('Output must be a new file; existing EFI is never overwritten')
    source = plistlib.loads(args.input.read_bytes())
    try:
        result = configure(source, args.mode, args.build, args.unmask_rp06)
    except ValueError as error:
        parser.error(str(error))
    with args.output.open('xb') as stream:
        plistlib.dump(result, stream, sort_keys=False)
    print('Created config copy. Copy the corresponding kexts, run matching ocvalidate, and review before installing.')
