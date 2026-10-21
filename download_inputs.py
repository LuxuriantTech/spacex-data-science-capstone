from pathlib import Path
import datetime, hashlib, json, urllib.request
HERE=Path(__file__).resolve().parent
DATA=HERE/'data'; DATA.mkdir(exist_ok=True)
records=[]
for s in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8')):
    dest=DATA/s['name']
    status=None
    source_mode='verified_cache'
    if not dest.exists():
        request=urllib.request.Request(s['url'],headers={'User-Agent':'SpaceX-educational-reproduction/1.0'})
        with urllib.request.urlopen(request,timeout=45) as response:
            payload=response.read()
            status=response.status
        source_mode='downloaded'
        if hashlib.sha256(payload).hexdigest()!=s['sha256']:raise RuntimeError('Upstream bytes changed: '+s['name'])
        dest.write_bytes(payload)
    if hashlib.sha256(dest.read_bytes()).hexdigest()!=s['sha256']:raise RuntimeError('Input hash mismatch: '+s['name'])
    records.append({**s,'path':str(dest),'bytes':dest.stat().st_size,'status':status,'source_mode':source_mode,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
(HERE/'DATA_ACQUISITION.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Verified',len(records),'exact input files')
