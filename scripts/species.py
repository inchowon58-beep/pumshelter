import json
import pathlib
from collections import Counter
pets = json.loads(pathlib.Path(r"f:\강아지보호소품으로\data\pets.json").read_text(encoding="utf-8"))
c = Counter(p.get("species") or "없음" for p in pets)
lines = [f"{n}\t{name}" for name, n in c.most_common()]
pathlib.Path(r"f:\강아지보호소품으로\data\species.txt").write_text("\n".join(lines), encoding="utf-8")
print(len(c))
