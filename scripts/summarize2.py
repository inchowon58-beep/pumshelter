import json
import pathlib
from collections import Counter

pets = json.loads(pathlib.Path(r"f:\강아지보호소품으로\data\pets.json").read_text(encoding="utf-8"))
lines = []
lines.append("health " + str(Counter(p.get("healthStatus") for p in pets)))
lines.append("intake " + str(Counter(p.get("intakeRoute") for p in pets)))
lines.append("species " + str(len(Counter(p.get("species") for p in pets))))
names = Counter(p["name"] for p in pets)
dups = [n for n, c in names.items() if c > 1]
lines.append("dup names " + ", ".join(dups))
lines.append("HIDDEN")
for p in pets:
    if p.get("status") == "hidden":
        lines.append(f"- {p['name']} {p.get('species')} {p.get('age')} {p['_id']}")
# image overlap for jjong
jj = next(p for p in pets if p["_id"].startswith("8cbb1b29"))
lines.append("main " + jj["photoUrl"])
for ph in jj["photos"]:
    lines.append("extra " + ph["url"] + " same=" + str(ph["url"] == jj["photoUrl"]))
pathlib.Path(r"f:\강아지보호소품으로\data\summary2.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
