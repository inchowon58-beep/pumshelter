"""Summarize one cafe article JSON so we know which fields to keep."""
import json
import pathlib

path = pathlib.Path(r"f:\강아지보호소품으로\data\cafe-probe\sample-v4.json")
data = json.loads(path.read_text(encoding="utf-8"))
article = data["result"]["article"]
lines = []
def log(*parts):
    lines.append(" ".join(str(part) for part in parts))

log("top", list(data["result"].keys()))
log("article", list(article.keys()))
log("subject", article.get("subject"))
content = article.get("contentHtml") or article.get("content") or ""
log("content type", type(content).__name__, "len", len(content) if isinstance(content, str) else "")
if isinstance(content, str):
    (path.parent / "content-sample.html").write_text(content, encoding="utf-8")
    log(content[:1800])
else:
    log(json.dumps(content, ensure_ascii=False)[:1800])
for key in ("images", "imageList", "attachImages", "representImage", "movies"):
    if key in article:
        value = article[key]
        log("FIELD", key, type(value).__name__, str(value)[:400])
# walk for image-like keys
found = []

def walk(node, trail):
    if isinstance(node, dict):
        for key, value in node.items():
            if "image" in key.lower() or "url" in key.lower() or key in {"src", "path"}:
                found.append((trail + "/" + key, str(value)[:180]))
            if len(found) < 40:
                walk(value, trail + "/" + key)
    elif isinstance(node, list) and node and len(found) < 40:
        walk(node[0], trail + "[0]")

walk(article, "article")
log("--- image-ish ---")
for item in found[:40]:
    log(item[0], item[1])
out = pathlib.Path(r"f:\강아지보호소품으로\data\cafe-probe\inspect.txt")
out.write_text("\n".join(lines), encoding="utf-8")
