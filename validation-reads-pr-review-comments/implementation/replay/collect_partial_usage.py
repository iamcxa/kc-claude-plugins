import json
from pathlib import Path

R=Path(__file__).resolve().parent
for meta_path in (R/'runs').glob('*/meta.json'):
    meta=json.loads(meta_path.read_text())
    if not meta.get('end') or meta.get('tokens') is not None:continue
    source=meta_path.parent/'events.jsonl'
    usage=[]
    for i,line in enumerate(source.read_text().splitlines(),1):
        try:event=json.loads(line)
        except ValueError:continue
        message=event.get('message',{})
        if event.get('type')=='assistant' and message.get('usage'):
            usage.append({'event_line':i,'message_id':message.get('id'),'model':message.get('model'),'usage':message['usage']})
    if usage:
        data={'scope':'Raw per-message usage snapshots only; no final CLI total returned. Snapshots may repeat a message id and are not summed.','source':'events.jsonl','events':usage}
        (meta_path.parent/'partial-usage.json').write_text(json.dumps(data,indent=2)+'\n')
        meta['partial_usage_file']='partial-usage.json'
        meta_path.write_text(json.dumps(meta,indent=2)+'\n')
