"""Download the ten Agapet daily-life posts into local story files."""
import json
import pathlib
import re
import urllib.request
from html.parser import HTMLParser

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
OUT = ROOT / "data" / "stories.json"
PHOTO_ROOT = ROOT / "site" / "stories"
LIST_URL = (
    "https://apis.naver.com/cafe-web/cafe2/ArticleListV2dot1.json"
    "?search.clubid=31765153&search.menuid=2&search.queryType=lastArticle&search.page=1&search.perPage=20"
)
ARTICLE_URL = "https://article.cafe.naver.com/gw/v4/cafes/31765153/articles/{article_id}?useCafeId=true&requestFrom=A"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://cafe.naver.com/agaetstory",
}
PREFIX = re.compile(r"^\[[^\]]+\]\s*")


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read()


class Blocks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.skip = 0
        self.in_p = False
        self.buf = []
        self.lines = []
        self.images = []

    def flush_text(self) -> None:
        if self.lines:
            self.blocks.append({"type": "text", "lines": self.lines})
            self.lines = []

    def flush_images(self) -> None:
        if self.images:
            self.blocks.append({"type": "images", "urls": self.images})
            self.images = []

    def handle_starttag(self, tag, attrs):
        attr = {key: value or "" for key, value in attrs}
        classes = attr.get("class", "")
        if tag == "script":
            raw = attr.get("data-module") or ""
            if '"v2_video"' in raw or '"type":"v2_video"' in raw or '"type": "v2_video"' in raw:
                try:
                    payload = json.loads(raw)
                    video = payload.get("data") or {}
                    if video.get("vid") and video.get("thumbnail"):
                        self.flush_text()
                        self.flush_images()
                        caption = (video.get("mediaMeta") or {}).get("title") or ""
                        self.blocks.append(
                            {
                                "type": "video",
                                "vid": video["vid"],
                                "inkey": video.get("inkey") or "",
                                "thumb": video["thumbnail"],
                                "caption": caption,
                            }
                        )
                except json.JSONDecodeError:
                    pass
            self.skip += 1
            return
        if tag == "style":
            self.skip += 1
            return
        if self.skip:
            return
        if tag == "p" and "se-text-paragraph" in classes:
            self.flush_images()
            self.in_p = True
            self.buf = []
        if tag == "br" and self.in_p:
            self.buf.append("\n")
        if tag == "img":
            src = attr.get("src", "")
            if not src or "cafe_profile" in src or "/static/cafe/" in src:
                return
            if "se-image-resource" in classes or "se-video" in classes or "thumbnail" in classes or "pstatic.net" in src:
                self.flush_text()
                clean = src.split("?")[0]
                if clean not in self.images:
                    self.images.append(clean)

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1
            return
        if self.skip:
            return
        if tag == "p" and self.in_p:
            text = "".join(self.buf).replace("\u200b", "").replace("\ufeff", "").strip()
            self.in_p = False
            self.buf = []
            if text:
                self.lines.extend(
                    line.strip()
                    for line in text.split("\n")
                    if line.replace("\u200b", "").replace("\ufeff", "").strip()
                )

    def handle_data(self, data):
        if self.skip or not self.in_p:
            return
        self.buf.append(data)

    def finish(self):
        self.flush_text()
        self.flush_images()
        return self.blocks


def download(url: str, dest: pathlib.Path) -> None:
    if dest.exists() and dest.stat().st_size > 1000:
        return
    sized = url if "image.nmv" in url or url.endswith(".mp4") else url + "?type=w1280"
    dest.write_bytes(get(sized))


def download_video(vid: str, inkey: str, dest: pathlib.Path) -> None:
    if dest.exists() and dest.stat().st_size > 10000:
        return
    api = f"https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{vid}?key={inkey}"
    payload = json.loads(get(api).decode("utf-8"))
    options = {item.get("encodingOption", {}).get("name"): item for item in payload["videos"]["list"]}
    chosen = options.get("480p") or options.get("270p") or options.get("720p")
    if not chosen or not chosen.get("source"):
        raise ValueError("no video source")
    dest.write_bytes(get(chosen["source"]))


def main() -> None:
    listing = json.loads(get(LIST_URL).decode("utf-8"))
    articles = listing["message"]["result"]["articleList"]
    stories = []
    for item in articles:
        article_id = str(item["articleId"])
        payload = json.loads(get(ARTICLE_URL.format(article_id=article_id)).decode("utf-8"))
        article = payload["result"]["article"]
        title = PREFIX.sub("", article.get("subject") or "").strip()
        parser = Blocks()
        parser.feed(article.get("contentHtml") or "")
        blocks = parser.finish()
        folder = PHOTO_ROOT / article_id
        folder.mkdir(parents=True, exist_ok=True)
        saved = {}
        index = 1
        local_blocks = []
        for block in blocks:
            if block["type"] == "text":
                if block["lines"]:
                    local_blocks.append(block)
                continue
            if block["type"] == "video":
                rel = f"stories/{article_id}/video.mp4"
                poster_rel = f"stories/{article_id}/poster.jpg"
                try:
                    download_video(block["vid"], block["inkey"], ROOT / "site" / rel)
                    download(block["thumb"], ROOT / "site" / poster_rel)
                except Exception as exc:
                    print(f"skip video {article_id} {exc}", flush=True)
                    continue
                local_blocks.append({"type": "video", "file": rel, "poster": poster_rel, "caption": block.get("caption") or ""})
                continue
            files = []
            for url in block["urls"]:
                if url in saved:
                    files.append(saved[url])
                    continue
                ext = pathlib.Path(url.split("?")[0]).suffix.lower()
                if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                    ext = ".jpg"
                rel = f"stories/{article_id}/{index:02d}{ext}"
                dest = ROOT / "site" / rel
                try:
                    download(url, dest)
                except Exception as exc:
                    print(f"skip image {article_id} {exc}", flush=True)
                    continue
                if dest.stat().st_size < 1000:
                    dest.unlink(missing_ok=True)
                    print(f"skip tiny {article_id} {rel}", flush=True)
                    continue
                saved[url] = rel
                files.append(rel)
                index += 1
            if files:
                local_blocks.append({"type": "images", "files": files})
        cover = next((block["files"][0] for block in local_blocks if block["type"] == "images"), "")
        stories.append({"id": article_id, "title": title, "cover": cover, "blocks": local_blocks})
        texts = sum(1 for block in local_blocks if block["type"] == "text")
        photos = sum(len(block["files"]) for block in local_blocks if block["type"] == "images")
        print(f"{article_id} photos {photos} texts {texts} {title}", flush=True)
    OUT.write_text(json.dumps(stories, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"stories {len(stories)}", flush=True)


if __name__ == "__main__":
    main()
