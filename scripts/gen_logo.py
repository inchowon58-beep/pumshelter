"""Original 강아지보호소 품으로 mark. Reads GEMINI_API_KEY from the environment."""
import base64
import json
import os
import pathlib
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
DEST = ROOT / "site" / "assets" / "logo"
MODEL = "gemini-3.1-flash-image"
PROMPT = (
    "Square app icon logo for a Korean dog shelter brand, flat vector, original, not cute clipart. "
    "Rounded square background in sage green #2f6b4a with subtle gradient. "
    "Center: ivory circle #fffdf9 with a minimal front-facing dog face—floppy ears, persimmon nose #e15a32, "
    "ink brown outlines #241c16, cream fur #f4efe6. Small persimmon star above the head (care mark, not text). "
    "No cat, no heart shape, no circle border frame, no house, no paw print only, no text, no letters, no watermark. "
    "Clean geometric shapes, readable at 54 pixels. Outside margin flat cream #f4efe6."
)


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
        mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
        ext = ".jpg" if "jpeg" in mime or "jpg" in mime else ".png"
        target = dest.with_suffix(ext)
        target.write_bytes(base64.b64decode(inline["data"]))
        print(f"image {target.name} {target.stat().st_size}", flush=True)
        return
    texts = [part.get("text", "") for part in parts]
    raise ValueError("no image " + " ".join(texts)[:240])


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    last_error = None
    for attempt in range(3):
        try:
            payload = post(
                {
                    "contents": [{"role": "user", "parts": [{"text": PROMPT}]}],
                    "generationConfig": {
                        "responseModalities": ["TEXT", "IMAGE"],
                        "imageConfig": {"aspectRatio": "1:1"},
                    },
                },
                api_key,
            )
            save_image(payload, DEST)
            try:
                from PIL import Image

                path = next(p for p in DEST.parent.glob("logo.*") if p.suffix in {".png", ".jpg", ".jpeg"})
                img = Image.open(path).convert("RGBA")
                w, h = img.size
                side = min(w, h)
                img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
                flat = Image.new("RGB", (side, side), "#f4efe6")
                flat.paste(img, mask=img.split()[3])
                flat.save(DEST.parent / "logo.jpg", quality=92)
                flat.resize((64, 64), Image.Resampling.LANCZOS).save(DEST.parent / "favicon.png")
            except ImportError:
                pass
            last_error = None
            break
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500] if isinstance(exc, urllib.error.HTTPError) else str(exc)
            last_error = detail
            print(f"retry {attempt + 1} {detail}", flush=True)
            time.sleep(2 + attempt)
    if last_error:
        raise SystemExit(last_error)
    print("done", flush=True)


if __name__ == "__main__":
    main()
