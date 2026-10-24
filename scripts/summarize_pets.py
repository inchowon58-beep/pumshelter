import json
import pathlib
from collections import Counter

pets = json.loads(
    pathlib.Path(r"f:\강아지보호소품으로\data\pets.json").read_text(encoding="utf-8")
)
lines = []
lines.append(f"count {len(pets)}")
genders = Counter(p.get("gender") for p in pets)
neutered = Counter(p.get("neutered") for p in pets)
status = Counter(p.get("status") for p in pets)
lines.append(f"gender {dict(genders)}")
lines.append(f"neutered {dict(neutered)}")
lines.append(f"status {dict(status)}")
photo_counts = Counter(len(p.get("photos") or []) for p in pets)
lines.append(f"extra photo counts {dict(photo_counts)}")
filled = {
    "description": sum(1 for p in pets if p.get("description")),
    "story": sum(1 for p in pets if p.get("story")),
    "note": sum(1 for p in pets if p.get("note")),
    "urgent": sum(1 for p in pets if p.get("urgent")),
    "traits": sum(1 for p in pets if p.get("traits")),
    "photoUrl": sum(1 for p in pets if p.get("photoUrl")),
}
lines.append(f"filled {filled}")
# show one waiting pet fully except long urls
sample = next(p for p in pets if p.get("status") == "waiting" and p.get("name") == "쫑이")
slim = {k: v for k, v in sample.items() if k not in ("photos", "photoUrl", "photoRef")}
slim["photoCount"] = len(sample.get("photos") or [])
lines.append("SAMPLE")
lines.append(json.dumps(slim, ensure_ascii=False, indent=2))
# trait length distribution
trait_n = Counter(len(p.get("traits") or []) for p in pets)
lines.append(f"trait counts {dict(trait_n)}")
# missing main photo
lines.append(f"missing main {sum(1 for p in pets if not p.get('photoUrl'))}")
pathlib.Path(r"f:\강아지보호소품으로\data\summary.txt").write_text(
    "\n".join(lines), encoding="utf-8"
)
print("wrote summary")
