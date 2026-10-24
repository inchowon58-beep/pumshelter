import pathlib
import re

root = pathlib.Path(r"f:\강아지보호소품으로\site")
samples = [
    root / "pets" / "pet-imported-511" / "index.html",
    root / "stories" / "11" / "index.html",
    root / "stories" / "3" / "index.html",
]
out = []
for path in samples:
    html = path.read_text(encoding="utf-8")
    texts = re.findall(r"<li><strong>(.*?)</strong><p>(.*?)</p></li>", html)
    wishes = [text for _, text in texts if any(word in text for word in ("좋은 가족", "잘 자라", "아프지 말"))]
    out.append(f"## {path.parent.name} {len(texts)} comments, wishes {len(wishes)}")
    for name, text in texts:
        mark = " *" if text in wishes or any(word in text for word in ("좋은 가족", "잘 자라", "아프지 말")) else ""
        out.append(f"- {name}: {text}{mark}")
    out.append("")
pathlib.Path(r"f:\강아지보호소품으로\data\wish-peek.txt").write_text("\n".join(out), encoding="utf-8")
