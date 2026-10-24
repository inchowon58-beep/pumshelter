import json
import pathlib
import urllib.request

url = "https://article.cafe.naver.com/gw/v4/cafes/31765153/articles/5?useCafeId=true&requestFrom=A"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://cafe.naver.com/agaetstory"})
with urllib.request.urlopen(req, timeout=30) as response:
    html = json.loads(response.read().decode("utf-8"))["result"]["article"]["contentHtml"]
start = html.find("se-video")
pathlib.Path(r"f:\강아지보호소품으로\data\story5-video.html").write_text(html[start - 200 : start + 2500], encoding="utf-8")

url4 = "https://article.cafe.naver.com/gw/v4/cafes/31765153/articles/4?useCafeId=true&requestFrom=A"
req = urllib.request.Request(url4, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://cafe.naver.com/agaetstory"})
with urllib.request.urlopen(req, timeout=30) as response:
    html4 = json.loads(response.read().decode("utf-8"))["result"]["article"]["contentHtml"]
start = html4.find("se-video")
pathlib.Path(r"f:\강아지보호소품으로\data\story4-video.html").write_text(
    "missing" if start < 0 else html4[start - 200 : start + 2500], encoding="utf-8"
)
