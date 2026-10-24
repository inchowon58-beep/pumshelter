import json
import pathlib
import urllib.request
from html.parser import HTMLParser

stories = json.loads(pathlib.Path(r"f:\강아지보호소품으로\data\stories.json").read_text(encoding="utf-8"))
lines = []
for story in stories:
    lines.append(f"#{story['id']} {story['title']} cover={story['cover']}")
    for block in story["blocks"]:
        if block["type"] == "text":
            lines.append("  T " + " / ".join(block["lines"][:4]))
        else:
            lines.append("  I " + ", ".join(block["files"]))
pathlib.Path(r"f:\강아지보호소품으로\data\stories-preview.txt").write_text("\n".join(lines), encoding="utf-8")

url = "https://article.cafe.naver.com/gw/v4/cafes/31765153/articles/5?useCafeId=true&requestFrom=A"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://cafe.naver.com/agaetstory"})
with urllib.request.urlopen(req, timeout=30) as response:
    html = json.loads(response.read().decode("utf-8"))["result"]["article"]["contentHtml"]
classes = []

class P(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        cls = attr.get("class") or ""
        if "se-component" in cls or "se-module" in cls or tag in {"video", "iframe", "source"}:
            classes.append(f"{tag} {cls[:120]} src={(attr.get('src') or '')[:80]}")

P().feed(html)
pathlib.Path(r"f:\강아지보호소품으로\data\story5-classes.txt").write_text("\n".join(classes), encoding="utf-8")
