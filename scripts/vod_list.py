import json
import pathlib

data = json.loads(pathlib.Path(r"f:\강아지보호소품으로\data\vod.json").read_text(encoding="utf-8"))
lines = []
for item in data["videos"]["list"]:
    lines.append(
        f"{item.get('encodingOption', {}).get('name')} {item.get('size')} {item.get('duration')} {(item.get('source') or '')[:180]}"
    )
pathlib.Path(r"f:\강아지보호소품으로\data\vod-list.txt").write_text("\n".join(lines), encoding="utf-8")
