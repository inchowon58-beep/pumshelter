"""Write the surrender section copy and step images with Gemini."""
import base64
import json
import os
import pathlib
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
COPY_PATH = ROOT / "data" / "rehome.json"
IMAGE_DIR = ROOT / "site" / "assets" / "rehome"
TEXT_MODEL = "gemini-3.8-flash"
IMAGE_MODEL = "gemini-3.1-flash-image"

FACTS = """
강아지 파양은 개인적인 사정으로 더 이상 아이와 함께할 수 없을 때, 아이를 입소시키고 무료 분양으로 새로운 가족을 찾아 주는 과정이다.
파양 사유는 다양하다. 예를 들면 이민, 군 입대, 알러지, 보호자 부재다.
아이에게 마지막으로 줄 수 있는 선물은 새로운 가족을 찾아 주는 것이다.
아이들에게 새로운 가족을 만날 기회를 주는 일이다.
절차:
1. 상담으로 나이, 지역, 질병 유무 등 기본 정보와 특이 상황을 확인하고, 입소 가능 여부를 1차로 본다. 입소는 무조건 되지 않는다. 아이들이 지낼 공간이 필요해서 센터 상황을 확인한 뒤 결정한다.
2. 센터 직접 방문 또는 픽업을 정한다. 전국 어디든 담당자가 무료로 픽업한다.
3. 입소 동의서를 작성한다. 비용과 동의 사항 등 확인 사항을 본 뒤 작성한다. 구체적인 금액은 쓰지 말 것.
4. 건강 상태, 대형견·소형견·노령견 여부를 확인한 뒤 아이가 지낼 센터가 정해진다.
5. 입소 후 사진과 동영상을 촬영해 새로운 가족을 만나기 위한 준비를 한다.
6. 입양 공고를 통해 새로운 가족을 만난다.
전화 상담 번호는 0505-707-0401 이다.
"""

COPY_PROMPT = f"""강아지보호소 품으로 홈페이지에 넣을 한국어 글을 작성하세요.
문체는 담백하고 단정하게. 과장된 광고 문구, 느낌표, 다른 업체 이름은 쓰지 마세요.
다음 단어는 쓰지 마세요: 기부, 후원, 봉사, 봉사활동, 안락사, 안락사없는.
네이버 유사문서를 피하려고 흔한 보호소 문장과 다른 표현을 쓰세요.
아래 사실만 사용하고 금액, 기간, 성공 보장은 만들지 마세요.
제목은 '강아지 파양 입소'로 하세요.
소개는 2문단. 마지막 문장은 아이에게 새로운 가족을 만날 기회를 준다는 마음으로 닫으세요.
사유 예시는 배열로: 이민, 군 입대, 알러지, 보호자 부재.
한 줄 문장은 새로운 가족을 찾아 주는 일이 아이에게 줄 수 있는 마지막 선물임을 담으세요.
절차는 6단계. 각 제목은 8자 안팎, 본문은 두 문장으로 짧게.
출력은 JSON만.
형식:
{{"title":"","intro":["",""],"reasons":[{{"title":"","body":"","image":"reason-01"}}],"cases":["",""],"quote_lines":[{{"text":"","size":"sm"}}],"steps":[{{"title":"","body":""}}]}}
reasons는 4개 객체. image는 reason-01~reason-04. cases는 6개. quote_lines는 4줄(size는 sm/md/lg).
intro는 rich markup {{c}} {{/c}} {{u}} {{/u}} 사용 가능.

사실:
{FACTS}
"""

STYLE = (
    "Editorial photograph for a refined animal shelter website. Warm ivory walls, pale oak, linen, "
    "soft afternoon window light, muted sage and a hint of persimmon, 35mm film, shallow depth of field, "
    "quiet and dignified. No text, no letters, no logos, no watermark, no cartoon, no collage."
)

IMAGES = [
    (
        "01",
        "A Korean adult in simple neutral clothes sits beside a sunlit window, speaking calmly on a phone. "
        "A small dog rests on a linen sofa nearby. The face is turned slightly away. Intimate and respectful.",
    ),
    (
        "02",
        "At a quiet residential doorway in soft daylight, a caregiver in plain clothes kneels and gently receives "
        "a small dog. The moment is dignified, not tearful. No uniforms, no logos, no readable signs.",
    ),
    (
        "03",
        "Hands signing a completely blank cream sheet on a pale oak table, a ceramic cup nearby. "
        "A dog is softly out of focus at the edge of the frame. No writing, no letters, no stamps.",
    ),
    (
        "04",
        "A peaceful upscale shelter room with low wooden beds and cream blankets. One small dog and one calm "
        "larger senior dog rest separately. Plants, soft light, no metal cage stacks, no sadness.",
    ),
    (
        "05",
        "A small white dog sits calmly on linen while a person photographs it with a simple camera. "
        "Warm editorial light, tasteful, the dog looks comfortable. No text on the backdrop.",
    ),
    (
        "06",
        "A person sits on a pale wood floor as a dog leans gently into their hands. Quiet hope, natural light, "
        "not a posed smile at the camera. No text, no logos.",
    ),
]


def post(model: str, body: dict, api_key: str) -> dict:
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.load(response)


def write_copy(api_key: str, force: bool = False) -> None:
    if COPY_PATH.exists() and not force:
        print("copy exists", flush=True)
        return
    payload = post(
        TEXT_MODEL,
        {
            "contents": [{"role": "user", "parts": [{"text": COPY_PROMPT}]}],
            "generationConfig": {"temperature": 0.6, "responseMimeType": "application/json"},
        },
        api_key,
    )
    text = payload["candidates"][0]["content"]["parts"][0]["text"]
    data = json.loads(text[text.find("{") : text.rfind("}") + 1])
    if len(data.get("steps") or []) != 6:
        raise SystemExit(f"expected 6 steps, got {len(data.get('steps') or [])}")
    COPY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("copy saved", flush=True)


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
    raise ValueError("no image " + " ".join(texts)[:300])


def write_images(api_key: str) -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    for name, scene in IMAGES:
        if any((IMAGE_DIR / f"{name}{ext}").exists() for ext in (".jpg", ".png", ".webp")):
            print(f"skip {name}", flush=True)
            continue
        last_error = None
        for attempt in range(3):
            try:
                payload = post(
                    IMAGE_MODEL,
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


def main() -> None:
    import sys

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing")
    write_copy(api_key, force="--force" in sys.argv)
    write_images(api_key)
    print("done", flush=True)


if __name__ == "__main__":
    main()
