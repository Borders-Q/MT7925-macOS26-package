import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('configure',ROOT/'scripts/configure.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.original={'PlatformInfo':{'Generic':{'SystemSerialNumber':'SYNTHETIC-TEST-ONLY'}},
            'ACPI':{'Add':[{'Path':'SSDT-Disable_Network_RP06.aml','Enabled':True},
                           {'Path':'SSDT-EC.aml','Enabled':True}]},
            'Kernel':{'Add':[dict(module.kext_entry('Lilu'),MinKernel='',MaxKernel=''),
                             module.kext_entry('VirtualSMC')]},
            'NVRAM':{'Add':{module.GUID:{'boot-args':'-v debug=0x100 mtkfe=native mtknativeif=1'}},
                     'Delete':{module.GUID:['existing-key']}}}

    def test_preserves_unrelated_settings_and_original(self):
        before=copy.deepcopy(self.original)
        result=module.configure(self.original)
        self.assertEqual(self.original,before)
        self.assertEqual(result['PlatformInfo'],before['PlatformInfo'])
        self.assertEqual(result['ACPI'],before['ACPI'])
        self.assertIn('debug=0x100',result['NVRAM']['Add'][module.GUID]['boot-args'])
        self.assertNotIn('mtkfe=',result['NVRAM']['Add'][module.GUID]['boot-args'])
        self.assertEqual(result['NVRAM']['Add'][module.GUID]['bluetoothInternalControllerInfo'],bytes(14))
        entries=result['Kernel']['Add']
        self.assertEqual(entries[0]['BundlePath'],'Lilu.kext')
        self.assertEqual(entries[0]['MinKernel'],'')
        self.assertEqual(sum(e['BundlePath']=='Lilu.kext' for e in entries),1)
        self.assertFalse(next(e for e in entries if e['BundlePath']=='LegionBtFix.kext')['Enabled'])

    def test_native_requires_exact_supported_build(self):
        for build in ('','25G74','25G999'):
            with self.assertRaises(ValueError):module.configure(self.original,'native',build)
        for build in module.NATIVE_BUILDS:
            result=module.configure(self.original,'native',build)
            self.assertTrue(next(e for e in result['Kernel']['Add'] if e['BundlePath']=='MtkWlanNative.kext')['Enabled'])
            self.assertTrue(next(e for e in result['Kernel']['Add'] if e['BundlePath']=='LegionBtFix.kext')['Enabled'])

    def test_repeated_merge_does_not_duplicate_entries_or_bootargs(self):
        first=module.configure(self.original,'native','25G241')
        self.assertEqual(module.configure(first,'native','25G241'),first)

    def test_board_specific_unmask_is_explicit(self):
        result=module.configure(self.original,unmask_rp06=True)
        self.assertFalse(result['ACPI']['Add'][0]['Enabled'])
        self.assertTrue(result['ACPI']['Add'][1]['Enabled'])
        with self.assertRaises(ValueError):module.configure({},unmask_rp06=True)

    def test_competing_driver_requires_review(self):
        self.original['Kernel']['Add'].append(module.kext_entry('itlmt7925'))
        with self.assertRaises(ValueError):module.configure(self.original)


if __name__=='__main__':unittest.main()
