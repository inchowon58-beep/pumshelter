"""Write a short adoption blurb for each public pet with the Gemini API."""
import json
import os
import pathlib
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
PETS_PATH = ROOT / "data" / "pets.json"
OUT_PATH = ROOT / "data" / "blurbs.json"
MODEL = "gemini-3.8-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

PROMPT = """당신은 동물보호소 입양 소개 글을 씁니다.
각 아이에 대해 한국어로 2문장, 70~120자 안으로 짧게 쓰세요.
주어진 특징을 그대로 살리되, 읽은 사람이 전화로 한번 만나보고 싶게 따뜻하고 담백하게 쓰세요.
없는 성격, 건강, 나이는 만들지 마세요.
입양 대기, 입양 완료, 보호 시작일, 입소 경로는 쓰지 마세요.
기부, 후원, 봉사, 안락사 같은 단어는 쓰지 마세요.
다른 보호소와 겹치는 흔한 문장(예: '천사 같은 아이', '운명의 만남')은 피하세요.
출력은 JSON 배열만 반환하세요. 설명이나 코드블록은 붙이지 마세요.
형식: [{"id":"아이디","blurb":"소개글"}]
"""


def public_pets() -> list[dict]:
    raw = json.loads(PETS_PATH.read_text(encoding="utf-8"))
    pets = []
    for pet in raw:
        if pet.get("status") not in ("waiting", "adopted"):
            continue
        pets.append(
            {
                "id": pet["_id"],
                "name": pet.get("name") or "",
                "species": pet.get("species") or "",
                "age": pet.get("age") or "",
                "gender": {"male": "남아", "female": "여아"}.get(pet.get("gender"), ""),
                "health": pet.get("healthStatus") or "",
                "traits": [trait for trait in (pet.get("traits") or []) if trait],
            }
        )
    return pets


def extract_json(text: str) -> list[dict]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0]
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start < 0 or end < start:
        raise ValueError(cleaned[:300])
    return json.loads(cleaned[start : end + 1])


def ask(batch: list[dict], api_key: str) -> list[dict]:
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": PROMPT + "\n아이들:\n" + json.dumps(batch, ensure_ascii=False)}],
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json",
        },
    }
    request = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = json.load(response)
    text = payload["candidates"][0]["content"]["parts"][0]["text"]
    return extract_json(text)


def main() -> None:
    import sys

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing")
    pets = public_pets()
    blurbs: dict[str, str] = {}
    force = "--force" in sys.argv
    if OUT_PATH.exists() and not force:
        blurbs.update(json.loads(OUT_PATH.read_text(encoding="utf-8")))
    pending = pets if force else [pet for pet in pets if not blurbs.get(pet["id"])]
    if force:
        blurbs = {}
    print(f"pets {len(pets)} pending {len(pending)}", flush=True)
    for index in range(0, len(pending), 8):
        batch = pending[index : index + 8]
        last_error = None
        for attempt in range(3):
            try:
                rows = ask(batch, api_key)
                for row in rows:
                    pet_id = row.get("id")
                    text = (row.get("blurb") or "").strip()
                    if pet_id and text:
                        blurbs[pet_id] = text
                OUT_PATH.write_text(json.dumps(blurbs, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"saved {min(index + 8, len(pending))}/{len(pending)}", flush=True)
                last_error = None
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError, KeyError) as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:400] if isinstance(exc, urllib.error.HTTPError) else str(exc)
                last_error = detail
                print(f"retry {attempt + 1} {detail}", flush=True)
                time.sleep(2 + attempt * 2)
        if last_error:
            raise SystemExit(last_error)
        time.sleep(0.4)
    missing = [pet["name"] for pet in pets if not blurbs.get(pet["id"])]
    print(f"done {len(blurbs)} missing {len(missing)}")
    if missing:
        print(", ".join(missing))


if __name__ == "__main__":
    main()
