"""Regenerate people photos so the people are Korean, and add reason images."""
import base64
import os
import pathlib
import time
import urllib.error
import urllib.request
import json

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
IMAGE_DIR = ROOT / "site" / "assets" / "rehome"
MODEL = "gemini-3.1-flash-image"
STYLE = (
    "Editorial photograph for a refined Korean animal shelter website. Warm ivory walls, pale oak, linen, "
    "soft afternoon window light, muted sage and a hint of persimmon, 35mm film, shallow depth of field, "
    "quiet and dignified. The person is Korean, with natural Korean features, not a celebrity, face in three-quarter view. "
    "No text, no letters, no logos, no watermark, no cartoon."
)
IMAGES = [
    (
        "02",
        "At a quiet Korean apartment doorway, one Korean woman kneels and a small dog stands on all four paws facing her. The dog's legs and paws are separate and natural. No extra hands, no second person. Dignified, not tearful.",
    ),
    (
        "05",
        "A Korean adult photographs a small white dog sitting calmly on linen. Warm editorial light. The person holds a simple camera. No text on the backdrop.",
    ),
    (
        "06",
        "A Korean adult sits on a pale wood floor as a dog leans gently into their hands. Quiet hope, natural light, not a posed smile.",
    ),
    (
        "reason-01",
        "A pregnant Korean woman sits by a sunlit window with a small dog resting at her feet. Calm, respectful, not medical.",
    ),
    (
        "reason-02",
        "A Korean adult sits indoors, a small dog a short distance away on a linen sofa. Quiet and serious, suggesting an allergy has made living together difficult. No sneezing, no medicine bottles with labels.",
    ),
    (
        "reason-03",
        "A Korean adult kneels beside a closed suitcase at a doorway and rests a hand on a small dog. The mood is a move or a long departure. No tickets, no readable signs.",
    ),
    (
        "reason-04",
        "An elderly Korean person sits beside an older grey-muzzled dog in warm window light. Respectful and tender, not pitiful.",
    ),
]


def post(body: dict, api_key: str) -> dict:
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.load(response)


def save_image(payload: dict, dest: pathlib.Path) -> None:
    parts = payload["candidates"][0]["content"]["parts"]
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if not inline:
            continue
        mime = inline.get("mimeType") or inline.get("mime_type") or "image/jpeg"
        ext = ".jpg" if "jpeg" in mime or "jpg" in mime else ".png"
        target = dest.with_suffix(ext)
        for old in dest.parent.glob(dest.name + ".*"):
            if old.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} and old != target:
                old.unlink()
        target.write_bytes(base64.b64decode(inline["data"]))
        print(f"image {target.name} {target.stat().st_size}", flush=True)
        return
    texts = [part.get("text", "") for part in parts]
    raise ValueError("no image " + " ".join(texts)[:240])


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing")
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    for name, scene in IMAGES[:1]:
        last_error = None
        for attempt in range(3):
            try:
                payload = post(
                    {
                        "contents": [{"role": "user", "parts": [{"text": STYLE + " " + scene}]}],
                        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
                    },
                    api_key,
                )
                save_image(payload, IMAGE_DIR / name)
                last_error = None
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:400] if isinstance(exc, urllib.error.HTTPError) else str(exc)
                last_error = detail
                print(f"retry {name} {attempt + 1} {detail}", flush=True)
                time.sleep(2 + attempt)
        if last_error:
            raise SystemExit(last_error)
    print("done", flush=True)


if __name__ == "__main__":
    main()
