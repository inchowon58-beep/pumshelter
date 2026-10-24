import json
import pathlib

pets = json.loads(pathlib.Path(r"f:\강아지보호소품으로\data\pets.json").read_text(encoding="utf-8"))
blurbs = json.loads(pathlib.Path(r"f:\강아지보호소품으로\data\blurbs.json").read_text(encoding="utf-8"))
public = [p for p in pets if p.get("status") in {"waiting", "adopted"}]
lines = []
for pet in public[:8]:
    traits = pet.get("traits") or []
    lines.append(
        f"{pet.get('name')} | {pet.get('species')} | {pet.get('age')} | {pet.get('gender')} | {pet.get('healthStatus')} | {pet.get('neutered')} | {pet.get('intakeRoute')}"
    )
    lines.append("  traits: " + " / ".join(traits))
    lines.append("  blurb: " + (blurbs.get(pet["_id"]) or "")[:180])
counts = []
for pet in public:
    counts.append(len([t for t in (pet.get("traits") or []) if t]))
lines.append(f"pets {len(public)} traits min {min(counts)} max {max(counts)} avg {sum(counts)/len(counts):.1f}")
pathlib.Path(r"f:\강아지보호소품으로\data\pet-peek.txt").write_text("\n".join(lines), encoding="utf-8")
