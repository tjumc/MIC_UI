#!/usr/bin/env python3
"""Export migration inventories without accessing the legacy site."""
from pathlib import Path
from urllib.parse import urlsplit
import csv,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
manifest=json.loads((HERE/'data/source-manifest.json').read_text(encoding='utf-8'))
content=json.loads((HERE/'data/content.json').read_text(encoding='utf-8'))
out=ROOT/'docs/mic-v1';out.mkdir(parents=True,exist_ok=True)
route_map={urlsplit(r['source']).path:r['target'] for r in manifest['legacy_routes']}
exact={r['source']:r['target'] for r in manifest['legacy_routes']}
for paper in content['papers']:
 for link in paper.get('links',[]):
  old=link.get('original_url','');path=urlsplit(old).path
  if old and path in route_map:exact[old]=route_map[path]
with (out/'old-url-map.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['原站实际地址','迁移站目标（相对站点根目录）','备注'])
 w.writerow(['https://mic.tongji.edu.cn/','index.html','原站根目录显示英文首页；新站根目录默认中文，英文主页为 en/index.html'])
 for source,target in sorted(exact.items()):w.writerow([source,target,'同路径 .htm 文件为静态兜底跳转；站群规则须管理员确认'])
with (out/'image-inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['原站图片地址或内嵌图片摘要','出现页面','迁移状态'])
 for image in manifest['image_references']:w.writerow([image['source'],' | '.join(image['pages']),'图片留白；需课题组确认后处理'])
with (out/'attachment-inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['原站附件地址','原始链接文字','引用页面','迁移站状态'])
 for item in manifest['attachments']:w.writerow([item['url'],' | '.join(item['labels']),' | '.join(item['pages']),'保留原站直链；学校交付需将附件包迁入并替换链接'])
print('old URLs',len(exact)+1,'image references',len(manifest['image_references']),'attachment URLs',len(manifest['attachments']))
