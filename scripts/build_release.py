#!/usr/bin/env python3
"""Assemble a release from pinned upstream assets. Never reads or writes a live EFI."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import stat
import struct
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
COMPONENT_KEXTS = {'wifi':'MtkWlan', 'native':'MtkWlanNative', 'bluetooth':'MtkBt',
                   'btfix':'LegionBtFix', 'lilu':'Lilu', 'bluetool':'BlueToolFixup'}
PACKAGE_VERSION = '0.1.0-alpha.1'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_kext_binary(data):
    """Accept thin or universal kexts only when they contain an x86_64 kext slice."""
    if data[:4] == b'\xcf\xfa\xed\xfe':
        magic,cpu,_,kind = struct.unpack_from('<4I',data)
        return (magic,cpu,kind) == (0xfeedfacf,0x1000007,11)
    if data[:4] in (b'\xca\xfe\xba\xbe', b'\xca\xfe\xba\xbf'):
        magic,count = struct.unpack_from('>II',data)
        record_size = 32 if magic == 0xcafebabf else 20
        for index in range(count):
            at = 8 + index*record_size
            if magic == 0xcafebabf:
                cpu,_,offset,length,_,_ = struct.unpack_from('>IIQQII',data,at)
            else:
                cpu,_,offset,length,_ = struct.unpack_from('>IIIII',data,at)
            if cpu == 0x1000007 and offset+length <= len(data):
                return verify_kext_binary(data[offset:offset+length])
    return False


def safe_extract(archive, destination):
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as stream:
        if stream.testzip() is not None:
            raise ValueError('Invalid ZIP CRC: '+archive.name)
        for item in stream.infolist():
            target = (destination/item.filename).resolve()
            if not target.is_relative_to(destination):
                raise ValueError('Unsafe ZIP member')
        stream.extractall(destination)


def ensure_asset(component, cache):
    path = cache/component['asset']
    if path.exists() and sha256(path) == component['sha256']:
        return path
    cache.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix+'.partial')
    subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                    '--connect-timeout', '20', '--max-time', '600', '--retry', '2',
                    '--output', str(partial), component['url']], check=True)
    if sha256(partial) != component['sha256']:
        raise ValueError('Upstream asset SHA-256 mismatch: '+component['id'])
    partial.replace(path)
    return path


def write_hashes(directory):
    lines = []
    for path in sorted(directory.rglob('*')):
        if path.is_file() and path.name != 'SHA256SUMS':
            lines.append(sha256(path)+'  '+path.relative_to(directory).as_posix())
    (directory/'SHA256SUMS').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def write_zip(directory, output):
    # Fixed ZIP timestamps and modes make the container reproducible for identical inputs.
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
        for path in sorted(directory.rglob('*')):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(directory.name+'/'+path.relative_to(directory).as_posix(), (2026,10,30,0,0,0))
            executable = path.suffix == '.sh' or path.name == 'mtkwifi-recovery' or path.parent.name == 'MacOS'
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            stream.writestr(info, path.read_bytes())


def build(cache, destination):
    lock = json.loads((ROOT/'dependencies.lock.json').read_text(encoding='utf-8'))
    folder = destination/('mt7925-macos26-'+PACKAGE_VERSION)
    archive = Path(str(folder)+'.zip')
    if folder.exists() or archive.exists():
        raise ValueError('Release output already exists; choose a new --output directory')
    assets = {c['id']:ensure_asset(c, cache) for c in lock['components']}
    client = ROOT/'tools/bin/mtkwifi-recovery'
    if not client.is_file():
        raise ValueError('Build the recovery client first: python3 scripts/build_recovery.py')
    folder.mkdir(parents=True)
    for name in ('docs','examples','licenses','third_party','scripts','tests','tools'):
        shutil.copytree(ROOT/name,folder/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ('README.md','README.en.md','LICENSE','NOTICE.md','dependencies.lock.json','CHANGELOG.md','RELEASE_NOTES.md','CONTRIBUTING.md'):
        shutil.copy2(ROOT/name,folder/name)
    (folder/'Kexts').mkdir()
    evidence = []
    with tempfile.TemporaryDirectory(prefix='mt7925-release-') as temp:
        for component in lock['components']:
            source_archive = ROOT/component['source_archive']
            assert sha256(source_archive) == component['source_sha256']
            unpacked = Path(temp)/component['id']
            safe_extract(assets[component['id']], unpacked)
            name = COMPONENT_KEXTS[component['id']]
            source = next(unpacked.rglob(name+'.kext'))
            kext = folder/'Kexts'/(name+'.kext')
            shutil.copytree(source,kext)
            info = plistlib.loads((kext/'Contents/Info.plist').read_bytes())
            assert info['CFBundleVersion'] == component['version'], (name,info['CFBundleVersion'])
            binary = kext/'Contents/MacOS'/info['CFBundleExecutable']
            assert verify_kext_binary(binary.read_bytes()), name+' is missing an x86_64 kext slice'
            before = sha256(binary)
            if name == 'MtkWlan':
                personality = info['IOKitPersonalities']['MT7925 PCIe']
                personality['MtkAutoOpenSsids'] = []
                personality['MtkAutoNetworks'] = []
                personality['MtkPower'] = False
                (kext/'Contents/Info.plist').write_bytes(plistlib.dumps(info,sort_keys=False))
            evidence.append({'component':component['id'],'kext':name+'.kext','version':component['version'],
                             'upstream_archive_sha256':component['sha256'],'binary_sha256':before,
                             'binary_unchanged':sha256(binary)==before,'info_plist_sha256':sha256(kext/'Contents/Info.plist')})
            shutil.copy2(assets[component['id']],folder/'third_party'/component['asset'])
    (folder/'VALIDATION.json').write_text(json.dumps({'package_version':PACKAGE_VERSION,'checked_on':lock['checked_on'],
        'components':evidence,'wifi_plist_changes':{'MtkAutoOpenSsids':[],'MtkAutoNetworks':[],'MtkPower':False},
        'kernel_binaries':'Unmodified upstream release binaries; not rebuilt or independently hardware validated',
        'hardware_validation':'Pending on Alienware AC16251; no success claim',
        'native_build_allowlist':['25G241','25G332']},indent=2)+'\n',encoding='utf-8')
    write_hashes(folder)
    write_zip(folder, archive)
    with zipfile.ZipFile(archive) as stream:
        assert stream.testzip() is None
    archive.with_name(archive.name+'.sha256').write_text(sha256(archive)+'  '+archive.name+'\n',encoding='ascii')
    print('Release ready: '+archive.name)
    print('SHA256: '+sha256(archive))
    return folder,archive


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,default=ROOT/'.cache/downloads')
    parser.add_argument('--output',type=Path,default=ROOT/'dist')
    args=parser.parse_args()
    try:
        build(args.cache.resolve(),args.output.resolve())
    except (ValueError,AssertionError) as error:
        raise SystemExit(str(error))
