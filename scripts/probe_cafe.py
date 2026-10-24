"""Probe Naver cafe article body endpoints and save UTF-8 samples."""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
OUT = ROOT / "data" / "cafe-probe"
OUT.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://cafe.naver.com/agaetstory",
}

LIST = "https://apis.naver.com/cafe-web/cafe2/ArticleListV2dot1.json?search.clubid=31765153&search.menuid=2&search.queryType=lastArticle&search.page=1&search.perPage=20"


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


listing = json.loads(get(LIST).decode("utf-8"))
articles = listing["message"]["result"]["articleList"]
(OUT / "list.json").write_text(json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8")
print("count", len(articles))
for item in articles:
    print(item["articleId"], item["subject"], item["imageAttachCount"])

article_id = articles[0]["articleId"]
candidates = [
    f"https://article.cafe.naver.com/gw/v4/cafes/31765153/articles/{article_id}?useCafeId=true&requestFrom=A",
    f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/31765153/articles/{article_id}?useCafeId=true&requestFrom=A",
    f"https://apis.naver.com/cafe-web/cafe-articleapi/v3/cafes/31765153/articles/{article_id}?useCafeId=true&requestFrom=A",
    f"https://apis.naver.com/cafe-web/cafe-articleapi/v2/cafes/31765153/articles/{article_id}",
]
for url in candidates:
    try:
        body = get(url)
    except Exception as exc:
        print("FAIL", url, type(exc).__name__, exc)
        continue
    path = OUT / f"sample-{url.split('/')[4][:12]}.json"
    path.write_bytes(body)
    print("OK", path.name, len(body), body[:180])
