#!/usr/bin/env python3
"""Check the cross-built client format and ad-hoc signature page hashes, without running it."""
import hashlib
import json
from pathlib import Path
import struct


def verify(path):
    data=Path(path).read_bytes()
    magic,cpu,_,kind,count,size,_,_=struct.unpack_from('<8I',data)
    assert (magic,cpu,kind)==(0xfeedfacf,0x1000007,2),'Expected an x86_64 Mach-O executable'
    offset=32
    signature=None
    for _ in range(count):
        command,length=struct.unpack_from('<II',data,offset)
        assert length>=8 and offset+length<=len(data)
        if command==0x1d:
            signature=struct.unpack_from('<II',data,offset+8)
        offset+=length
    assert offset==32+size and signature
    start,length=signature
    blob=data[start:start+length]
    magic,_,count=struct.unpack_from('>III',blob)
    assert magic==0xfade0cc0
    pages=0
    for index in range(count):
        slot,where=struct.unpack_from('>II',blob,12+8*index)
        if slot!=0:
            continue
        directory=blob[where:]
        magic,_,_,flags,hash_offset,_,_,slots,limit=struct.unpack_from('>9I',directory)
        hash_size,hash_type,_,page=struct.unpack_from('>4B',directory,36)
        assert magic==0xfade0c02 and hash_type==2 and hash_size==32 and flags&2
        for index in range(slots):
            actual=hashlib.sha256(data[index*(1<<page):min((index+1)*(1<<page),limit)]).digest()
            assert actual==directory[hash_offset+index*32:hash_offset+(index+1)*32]
        pages+=slots
    assert pages>0
    return {'format':'x86_64 Mach-O executable','ad_hoc_signature_pages_verified':pages,
            'sha256':hashlib.sha256(data).hexdigest(),'execution_on_macOS':'not performed by this static check'}


if __name__=='__main__':
    path=Path(__file__).resolve().parents[1]/'tools/bin/mtkwifi-recovery'
    print(json.dumps(verify(path),indent=2))
