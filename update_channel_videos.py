#!/usr/bin/env python3
"""公式チャンネルの直近フィードを検証して一覧JSONに保存する。"""
import json, re, sys, time, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

CHANNEL='UCvoQlzEzqa6vQA8hq9GNNug'
FEED='https://www.youtube.com/feeds/videos.xml?channel_id='+CHANNEL
NS={'a':'http://www.w3.org/2005/Atom','yt':'http://www.youtube.com/xml/schemas/2015'}
OUTPUT=Path(__file__).resolve().parent/'channel-videos.json'

def parse(data):
    root=ET.fromstring(data)
    if root.tag!='{%s}feed'%NS['a'] or root.findtext('yt:channelId',namespaces=NS) not in (CHANNEL, CHANNEL[2:]):
        raise ValueError('フィードのチャンネルが一致しません')
    out=[]; seen=set()
    for entry in root.findall('a:entry',NS):
        vid=entry.findtext('yt:videoId',default='',namespaces=NS)
        title=entry.findtext('a:title',default='',namespaces=NS).strip()
        published=entry.findtext('a:published',default='',namespaces=NS)
        if entry.findtext('yt:channelId',namespaces=NS)!=CHANNEL or not re.fullmatch(r'[A-Za-z0-9_-]{11}',vid) or not title or len(title)>800 or vid in seen:
            raise ValueError('動画のチャンネル、ID、タイトルまたは重複が不正です')
        dt=datetime.fromisoformat(published.replace('Z','+00:00'))
        if dt.tzinfo is None: raise ValueError('日時にタイムゾーンがありません')
        seen.add(vid); out.append({'id':vid,'title':title,'publishedAt':published})
    if not out: raise ValueError('フィードが空です')
    return sorted(out,key=lambda x:x['publishedAt'],reverse=True)

def get():
    last=None
    for attempt in range(3):
        try:
            request=urllib.request.Request(FEED,headers={'User-Agent':'OriginiumAtlasChannelUpdater/1.0'})
            with urllib.request.urlopen(request,timeout=30) as response:
                data=response.read(2_000_001)
            if len(data)>2_000_000: raise ValueError('フィードが大きすぎます')
            return data
        except Exception as exc:
            last=exc
            if attempt<2: time.sleep(2**attempt)
    raise RuntimeError('公式フィードの取得に失敗しました') from last

def main():
    videos=parse(get())
    result={'schemaVersion':1,'channelId':CHANNEL,'channelUrl':'https://www.youtube.com/@ArknightsStaff_JP','lastCheckedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'videos':videos}
    tmp=OUTPUT.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(OUTPUT)
    print('公式の直近動画',len(videos),'件を確認しました')
if __name__=='__main__':
    try: main()
    except Exception as exc: print('更新失敗（以前の一覧を維持）:',exc,file=sys.stderr);sys.exit(1)
