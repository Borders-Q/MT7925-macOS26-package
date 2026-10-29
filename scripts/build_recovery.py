#!/usr/bin/env python3
"""Build the userspace recovery client; never installs a kext or changes EFI."""
import argparse
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def build(llvm_bin=None, output=None):
    output = Path(output or ROOT / 'tools/bin/mtkwifi-recovery').resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    sources = [ROOT/'tools/src/mtkwifi-recovery.c', ROOT/'tools/vendor/MtkCrypto.c']
    includes = ['-I' + str(ROOT/'tools/vendor')]
    common = ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
              '-ffile-prefix-map='+str(ROOT)+'=.']
    if platform.system() == 'Darwin' and not llvm_bin:
        subprocess.run(['clang', '-arch', 'x86_64', '-mmacosx-version-min=11.0',
                        *common, *includes, *map(str, sources), '-Wl,-S', '-o', str(output)], check=True)
        subprocess.run(['codesign', '-s', '-', '-f', '--identifier', 'mtkwifi-recovery', str(output)], check=True)
    elif llvm_bin:
        llvm = Path(llvm_bin)
        suffix = '.exe' if platform.system() == 'Windows' else ''
        clang = llvm/('clang'+suffix)
        linker = llvm/('ld64.lld'+suffix)
        with tempfile.TemporaryDirectory(prefix='mt7925-client-build-') as temp:
            scratch = Path(temp)
            objects = []
            for index, source in enumerate(sources):
                obj = scratch/f'{index}.o'
                subprocess.run([str(clang), '--target=x86_64-apple-macos11', *common,
                                '-fno-stack-protector', '-nostdinc', '-I'+str(ROOT/'tools/cross'),
                                *includes, '-c', str(source), '-o', str(obj)], check=True)
                objects.append(str(obj))
            subprocess.run([str(linker), '-arch', 'x86_64', '-platform_version', 'macos', '11.0', '26.0',
                            '-pie', '-dead_strip', '-S', '-adhoc_codesign', '-L'+str(ROOT/'tools/cross'),
                            '-lSystem', '-o', 'mtkwifi-recovery', *objects], cwd=scratch, check=True)
            shutil.copy2(scratch/'mtkwifi-recovery',output)
    else:
        raise SystemExit('Use macOS Command Line Tools, or pass --llvm-bin with clang and ld64.lld.')
    print(f'Built {output.name}: {output.stat().st_size} bytes (x86_64 macOS)')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--llvm-bin')
    parser.add_argument('--output')
    args = parser.parse_args()
    build(args.llvm_bin, args.output)
