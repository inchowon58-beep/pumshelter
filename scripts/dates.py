import json
import pathlib
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
pets = json.loads(pathlib.Path(r"f:\강아지보호소품으로\data\pets.json").read_text(encoding="utf-8"))
rows = []
for pet in pets:
    if pet.get("status") == "hidden":
        continue
    updated = datetime.fromisoformat(pet["_updatedAt"].replace("Z", "+00:00")).astimezone(KST)
    created = datetime.fromisoformat(pet["_createdAt"].replace("Z", "+00:00")).astimezone(KST)
    rows.append((updated, created, pet.get("rescueDate"), pet["name"], pet["status"]))
rows.sort(reverse=True)
lines = [f"{u:%Y-%m-%d} upd {c:%Y-%m-%d} cre {r} {n} {s}" for u, c, r, n, s in rows[:12]]
pathlib.Path(r"f:\강아지보호소품으로\data\dates.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
