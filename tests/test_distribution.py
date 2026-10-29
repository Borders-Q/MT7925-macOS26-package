import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import struct
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('release',ROOT/'scripts/build_release.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class DistributionTests(unittest.TestCase):
    def test_source_snapshots_match_pins_and_contain_license(self):
        lock=json.loads((ROOT/'dependencies.lock.json').read_text())
        for component in lock['components']:
            path=ROOT/component['source_archive']
            self.assertEqual(module.sha256(path),component['source_sha256'])
            with zipfile.ZipFile(path) as archive:
                self.assertIsNone(archive.testzip())
                self.assertTrue(any(n in archive.namelist() for n in ('LICENSE','LICENSE.txt')))
                self.assertFalse(any('.git/' in n or n.endswith('.env') for n in archive.namelist()))

    def test_rejects_zip_path_traversal(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);archive=root/'unsafe.zip'
            with zipfile.ZipFile(archive,'w') as stream:stream.writestr('../escaped','bad')
            with self.assertRaises(ValueError):module.safe_extract(archive,root/'extract')
            self.assertFalse((root/'escaped').exists())

    def test_accepts_intel_thin_and_universal_kexts_but_rejects_wrong_kind(self):
        thin=struct.pack('<8I',0xfeedfacf,0x1000007,3,11,0,0,0,0)
        fat=struct.pack('>II',0xcafebabe,1)+struct.pack('>IIIII',0x1000007,3,28,len(thin),0)+thin
        self.assertTrue(module.verify_kext_binary(thin))
        self.assertTrue(module.verify_kext_binary(fat))
        self.assertFalse(module.verify_kext_binary(struct.pack('<8I',0xfeedfacf,0x1000007,3,2,0,0,0,0)))

    def test_reproducible_archive_preserves_executable_mode(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);source=root/'bundle';source.mkdir()
            (source/'test.sh').write_text('#!/bin/bash\nexit 0\n')
            module.write_zip(source,root/'one.zip');module.write_zip(source,root/'two.zip')
            self.assertEqual(module.sha256(root/'one.zip'),module.sha256(root/'two.zip'))
            with zipfile.ZipFile(root/'one.zip') as stream:
                self.assertTrue((stream.getinfo('bundle/test.sh').external_attr>>16)&0o111)


if __name__=='__main__':unittest.main()
