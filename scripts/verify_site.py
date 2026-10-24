import pathlib
import re

site = pathlib.Path(r"f:\강아지보호소품으로\site")
html_files = list(site.rglob("*.html"))
missing = []
pages = 0
for path in html_files:
    text = path.read_text(encoding="utf-8")
    pages += 1
    for match in re.findall(r'(?:src|href)="([^"]+)"', text):
        if match.startswith(("http", "tel:", "#", "mailto:")):
            continue
        target = (path.parent / match.split("#")[0]).resolve()
        if not target.exists():
            missing.append(f"{path.name}: {match}")

jj = (site / "pets" / "8cbb1b29-d1c3-4e4b-891a-e7f5f31df167" / "index.html").read_text(encoding="utf-8")
checks = {
    "traits": "메롱 혓바닥이 매력포인트" in jj and "동안페이스" in jj and "조용히 곁에 다가와요" in jj,
    "facts": all(word in jj for word in ["말티즈", "6살", "남아", "건강함", "완료", "2026.09.13", "파양"]),
    "photos": jj.count("8cbb1b29-d1c3-4e4b-891a-e7f5f31df167/") >= 3,
    "no-current-on-story": 'index.html#story" aria-current' not in jj,
}
home = (site / "index.html").read_text(encoding="utf-8")
board = (site / "pets" / "index.html").read_text(encoding="utf-8")
hidden_ids = [
    "6f6dde14-48c5-4e67-b743-9936b5858c87",
    "bb9d1ef0-0536-4fb2-9827-d01457d315c8",
    "76ccd010-bfd8-49b3-b9d7-9ef66271b686",
]
public_html = "\n".join(path.read_text(encoding="utf-8") for path in html_files)
hidden_leaks = [item for item in hidden_ids if item in public_html]
report = [
    f"html {pages}",
    f"missing {len(missing)}",
    *missing[:20],
    f"checks {checks}",
    f"home stats {'85' in home and '26' in home and '59' in home}",
    f"board cards {board.count('data-pet')}",
    f"hidden leaks {hidden_leaks}",
    f"first board names",
]
names = re.findall(r'data-name="([^"]+)"', board)
report.append(", ".join(names[:8]))
pathlib.Path(r"f:\강아지보호소품으로\data\verify.txt").write_text("\n".join(report), encoding="utf-8")
print("\n".join(report))
