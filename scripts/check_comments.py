import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_site as site

raw = json.loads(pathlib.Path(r"f:\강아지보호소품으로\data\pets.json").read_text(encoding="utf-8"))
blurbs = json.loads(pathlib.Path(r"f:\강아지보호소품으로\data\blurbs.json").read_text(encoding="utf-8"))
public = [site.normalize(pet, blurbs) for pet in raw if pet.get("status") in site.STATUS]
stories = site.load_stories()
lines = []
short = []
for pet in public:
    data = site.engagement(pet["id"], site.pet_comment_lines(pet))
    count = len(data["comments"])
    if not 15 <= count <= 30 or not 80 <= data["likes"] <= 140:
        short.append(f"pet {pet['name']} likes {data['likes']} comments {count}")
for story in stories:
    data = site.engagement("story-" + story["id"], site.story_comment_lines(story))
    count = len(data["comments"])
    if not 15 <= count <= 30:
        short.append(f"story {story['id']} comments {count}")

wanted = {"로키", "달봉이", "초코", "밤"}
for pet in public:
    if pet["name"] in wanted:
        data = site.engagement(pet["id"], site.pet_comment_lines(pet))
        lines.append(f"## {pet['name']} {pet['species']} {pet['age']} {pet['gender']} | {pet['health']}")
        lines.append("traits: " + " / ".join(pet["traits"]))
        for item in data["comments"]:
            lines.append(f"- {item['name']}: {item['text']}")
        lines.append("")

for story in stories:
    if story["id"] in {"11", "3", "4"}:
        data = site.engagement("story-" + story["id"], site.story_comment_lines(story))
        lines.append(f"## story {story['id']} {story['title']}")
        for item in data["comments"][:8]:
            lines.append(f"- {item['name']}: {item['text']}")
        lines.append("")

lines.append("problems " + str(len(short)))
lines.extend(short)
pathlib.Path(r"f:\강아지보호소품으로\data\comment-check.txt").write_text("\n".join(lines), encoding="utf-8")
