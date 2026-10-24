import json
import pathlib

root = pathlib.Path(r"f:\강아지보호소품으로")
pets = json.loads((root / "data" / "pets.json").read_text(encoding="utf-8"))
blurbs = json.loads((root / "data" / "blurbs.json").read_text(encoding="utf-8"))
public = [pet for pet in pets if pet.get("status") in ("waiting", "adopted")]
ids = {pet["_id"] for pet in public}
names = {pet["_id"]: pet.get("name") for pet in public}
missing = [names[pet_id] + " " + pet_id for pet_id in ids if not blurbs.get(pet_id)]
extra = [key for key in blurbs if key not in ids]
lengths = sorted((len(text), names.get(key, key)) for key, text in blurbs.items())
lines = [
    f"public {len(public)} blurbs {len(blurbs)}",
    "missing " + " | ".join(missing),
    "extra " + " | ".join(extra),
    "longest",
]
lines.extend(f"{n} {name}" for n, name in lengths[-8:])
lines.append("shortest")
lines.extend(f"{n} {name}" for n, name in lengths[:5])
(root / "data" / "blurb-check.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
