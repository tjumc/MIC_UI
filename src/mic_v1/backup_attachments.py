#!/usr/bin/env python3
"""Back up inventoried MIC code/PDF downloads as opaque files, without extraction."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
import argparse,hashlib,json,re,time
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
dest=args.output.resolve()
if dest.exists():raise SystemExit('Output already exists; choose a new directory to avoid overwriting files.')
items=json.loads((HERE/'data/attachment-check-20261125.json').read_text(encoding='utf-8'))['attachments']
if len(items)!=48 or any(x.get('status')!=206 or not isinstance(x.get('bytes'),int) for x in items):raise SystemExit('Attachment inventory incomplete.')
if sum(x['bytes'] for x in items)>300*1024*1024:raise SystemExit('Backup exceeds the 300 MiB safety limit.')
dest.mkdir(parents=True)
def fetch(item):
 url=item['url'];parts=urlsplit(url);label=item['label'];suffix='.tar.gz' if label.lower().endswith('.tar.gz') else '.zip' if label.lower().endswith('.zip') else '.pdf' if label.lower().endswith('.pdf') else ''
 if parts.scheme!='https' or parts.hostname!='mic.tongji.edu.cn' or not parts.path.startswith('/_upload/article/files/') or not suffix or item['bytes']>70*1024*1024:return {**item,'backup_status':'excluded'}
 safe=re.sub(r'[^A-Za-z0-9._-]+','-',label).strip('.-') or 'attachment'+suffix
 name=hashlib.sha256(url.encode()).hexdigest()[:12]+'-'+safe;path=dest/name;part=dest/(name+'.part')
 for attempt in range(2):
  try:
   request=Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://mic.tongji.edu.cn/','Cache-Control':'no-cache'})
   digest=hashlib.sha256();total=0
   with urlopen(request,timeout=70) as response,part.open('wb') as f:
    if response.status!=200:raise ValueError('Unexpected status '+str(response.status))
    while True:
     chunk=response.read(512*1024)
     if not chunk:break
     total+=len(chunk)
     if total>item['bytes']:raise ValueError('Download larger than inventoried size.')
     digest.update(chunk);f.write(chunk)
   if total!=item['bytes']:raise ValueError(f'Incomplete download: {total}/{item["bytes"]}')
   part.replace(path)
   return {**item,'backup_status':'ok','file':name,'sha256':digest.hexdigest()}
  except Exception as exc:
   error=str(exc);part.unlink(missing_ok=True);time.sleep(1)
 return {**item,'backup_status':'failed','error':error}
results=[]
with ThreadPoolExecutor(max_workers=3) as pool:
 for future in as_completed([pool.submit(fetch,item) for item in items]):
  result=future.result();results.append(result);print(result['label'],result['backup_status'],flush=True)
(dest/'manifest.json').write_text(json.dumps({'attachments':sorted(results,key=lambda x:x['url'])},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
failed=[x for x in results if x['backup_status']!='ok']
if failed:raise SystemExit(f'{len(failed)} attachments were not backed up; inspect manifest.json.')
print('All attachments backed up without extraction.')
