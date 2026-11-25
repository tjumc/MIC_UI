#!/usr/bin/env python3
"""Build a portable school handoff ZIP with previously backed-up attachments.

Attachment archives are copied as opaque files: this script never extracts or executes them.
"""
from pathlib import Path
from html import escape
import argparse,csv,hashlib,io,json,posixpath,zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SITE=ROOT/'dist/mic-v1'
DOCS=ROOT/'docs/mic-v1'
parser=argparse.ArgumentParser();parser.add_argument('--attachments',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
backup=args.attachments.resolve();output=args.output.resolve()
if output.exists():raise SystemExit('Output already exists; choose a new path to avoid overwriting.')
items=json.loads((backup/'manifest.json').read_text(encoding='utf-8'))['attachments']
if len(items)!=48 or any(x.get('backup_status')!='ok' for x in items):raise SystemExit('Attachment backup is incomplete.')
for item in items:
 p=(backup/item['file']).resolve()
 if not p.is_relative_to(backup) or not p.is_file():raise SystemExit('Invalid backup path: '+item['file'])
 digest=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
 if p.stat().st_size!=item['bytes'] or digest.hexdigest()!=item['sha256']:raise SystemExit('Attachment verification failed: '+item['file'])
counts={x['url']:0 for x in items}
with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
 for path in sorted(SITE.rglob('*')):
  if not path.is_file():continue
  rel=path.relative_to(SITE);arc='site/'+rel.as_posix()
  if path.suffix.lower() in ('.html','.htm'):
   text=path.read_text(encoding='utf-8')
   for item in items:
    old='href="'+escape(item['url'],quote=True)+'"'
    newpath=posixpath.relpath('assets/downloads/'+item['file'],start=rel.parent.as_posix())
    n=text.count(old)
    if n: text=text.replace(old,'href="'+escape(newpath,quote=True)+'"');counts[item['url']]+=n
   z.writestr(arc,text.encode('utf-8'))
  else:z.write(path,arc)
 for item in items:z.write(backup/item['file'],'site/assets/downloads/'+item['file'])
 for path in sorted(DOCS.glob('*')):
  if path.name=='HANDOFF.md':
   text=path.read_text(encoding='utf-8').replace('当前网页保留原站附件直链，不包含附件实体；学校迁移前必须备份附件、上传到学校系统并替换链接。','此交付包的 site/assets/downloads/ 包含原始附件，网页附件链接已改为包内相对路径；Git 分支中的普通构建仍保留原站直链。')
   z.writestr('docs/HANDOFF.md',text.encode('utf-8'))
  else:z.write(path,'docs/'+path.name)
 buf=io.StringIO(newline='');w=csv.writer(buf);w.writerow(['原站地址','包内文件','原始名称','字节数','SHA-256','替换链接数'])
 for item in items:w.writerow([item['url'],'site/assets/downloads/'+item['file'],item['label'],item['bytes'],item['sha256'],counts[item['url']]])
 z.writestr('docs/attachment-package-map.csv',buf.getvalue().encode('utf-8-sig'))
 z.writestr('README.txt','MIC version 1 school handoff\nOpen site/index.html. See docs/HANDOFF.md and docs/attachment-package-map.csv.\nAttachments are original opaque files, not extracted or executed.\n'.encode())
missing=[url for url,n in counts.items() if n==0]
if missing:raise SystemExit('Some attachment links were not rewritten: '+', '.join(missing))
with zipfile.ZipFile(output) as z:
 if z.testzip() is not None:raise SystemExit('ZIP verification failed')
print('Handoff package:',output,'attachments:',len(items),'replaced links:',sum(counts.values()),'bytes:',output.stat().st_size)
