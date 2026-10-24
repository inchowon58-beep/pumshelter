"""Download resized pet photos from the shelter's Sanity CDN."""
import json
import pathlib
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
PETS_PATH = ROOT / "data" / "pets.json"
PHOTO_ROOT = ROOT / "site" / "photos"
MANIFEST_PATH = ROOT / "data" / "manifest.json"

WIDTH = 1280
QUALITY = 72


def resized(url: str) -> str:
    return f"{url}?w={WIDTH}&fit=max&q={QUALITY}&fm=jpg"


def unique_urls(pet: dict) -> list[str]:
    urls = []
    seen = set()
    main = pet.get("photoUrl")
    if main:
        urls.append(main)
        seen.add(main)
    for photo in pet.get("photos") or []:
        url = photo.get("url")
        if url and url not in seen:
            urls.append(url)
            seen.add(url)
    return urls


def download(item: tuple[str, pathlib.Path]) -> tuple[str, str, int]:
    url, dest = item
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return ("skip", str(dest), dest.stat().st_size)
    req = urllib.request.Request(resized(url), headers={"User-Agent": "lovemong-migrate/1.0"})
    with urllib.request.urlopen(req, timeout=60) as res:
        data = res.read()
    dest.write_bytes(data)
    return ("ok", str(dest), len(data))


def main() -> None:
    pets = json.loads(PETS_PATH.read_text(encoding="utf-8"))
    jobs = []
    manifest = []
    for pet in pets:
        urls = unique_urls(pet)
        local = []
        for index, url in enumerate(urls):
            dest = PHOTO_ROOT / pet["_id"] / f"{index}.jpg"
            jobs.append((url, dest))
            local.append(f"photos/{pet['_id']}/{index}.jpg")
        manifest.append({"id": pet["_id"], "photos": local})

    ok = skip = fail = total_bytes = 0
    failures = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(download, job): job for job in jobs}
        done = 0
        for future in as_completed(futures):
            done += 1
            url, dest = futures[future]
            try:
                status, _path, size = future.result()
                total_bytes += size
                if status == "ok":
                    ok += 1
                else:
                    skip += 1
            except Exception as exc:  # noqa: BLE001
                fail += 1
                failures.append({"url": url, "dest": str(dest), "error": str(exc)})
            if done % 25 == 0 or done == len(jobs):
                print(f"{done}/{len(jobs)} ok={ok} skip={skip} fail={fail}", flush=True)

    MANIFEST_PATH.write_text(
        json.dumps({"photos": manifest, "failures": failures}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"bytes {total_bytes} failures {len(failures)}")


if __name__ == "__main__":
    main()
