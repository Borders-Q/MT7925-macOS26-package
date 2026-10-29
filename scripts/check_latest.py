#!/usr/bin/env python3
"""Compare the lockfile with GitHub latest non-prerelease releases; never updates pins."""
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/'dependencies.lock.json').read_text(encoding='utf-8'))
for component in lock['components']:
    request=urllib.request.Request('https://api.github.com/repos/'+component['repo']+'/releases/latest',
                                  headers={'User-Agent':'MT7925-release-check','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(request,timeout=30) as response:
        release=json.load(response)
    latest=release['tag_name']
    if latest==component['version']:
        asset=next((a for a in release['assets'] if a['name']==component['asset']),None)
        unchanged=bool(asset and asset.get('digest')=='sha256:'+component['sha256'])
        status='current; asset hash unchanged' if unchanged else 'CHECK: release asset changed or unavailable'
    else:
        status='new release available; review before changing lockfile'
    print(f"{component['repo']}: pinned={component['version']} latest={latest} ({status})")
