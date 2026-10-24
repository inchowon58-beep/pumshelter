"""Export every pet document from the public Sanity dataset."""
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
OUT = ROOT / "data" / "pets.json"
QUERY = """
*[_type == "pet"]{
  _id,
  _createdAt,
  _updatedAt,
  name,
  age,
  gender,
  healthStatus,
  intakeRoute,
  neutered,
  order,
  species,
  status,
  traits,
  rescueDate,
  description,
  story,
  note,
  urgent,
  "photoRef": photo.asset._ref,
  "photoUrl": photo.asset->url,
  "photos": photos[]{
    "key": _key,
    "ref": asset._ref,
    "url": asset->url
  }
} | order(rescueDate desc, order asc)
""".strip()

url = (
    "https://58cgd16k.api.sanity.io/v2021-10-21/data/query/production?query="
    + urllib.parse.quote(QUERY)
)
req = urllib.request.Request(url, headers={"User-Agent": "lovemong-migrate/1.0"})
with urllib.request.urlopen(req, timeout=60) as res:
    payload = json.load(res)

pets = payload["result"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(pets, ensure_ascii=False, indent=2), encoding="utf-8")

keys = set()
for pet in pets:
    keys.update(pet.keys())
print("count", len(pets))
print("keys", sorted(keys))
statuses = {}
for pet in pets:
    statuses[pet.get("status")] = statuses.get(pet.get("status"), 0) + 1
print("status", statuses)
print("sample", pets[0]["name"], pets[0].get("species"), len(pets[0].get("photos") or []))
