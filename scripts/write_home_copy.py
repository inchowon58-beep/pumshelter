"""Refresh homepage hero and adoption step copy with Gemini."""
import json
import os
import pathlib
import urllib.request

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
DEST = ROOT / "data" / "home_copy.json"
MODEL = "gemini-3.8-flash"
ADOPT_PHONE = "0505-464-1004"
REHOME_PHONE = "0505-707-0401"

PROMPT = f"""
강아지보호소 품으로 메인 페이지 문구를 JSON만 출력하세요. 설명 문장은 쓰지 마세요.
문체는 담백하고 정보 위주. 느낌표, 과장, 다른 업체 이름은 금지.
다음 단어는 절대 쓰지 마세요: 기부, 후원, 봉사, 봉사활동, 안락사, 안락사없는.
입양 문의 전화는 {ADOPT_PHONE}, 파양 입소 상담은 {REHOME_PHONE}입니다.
네이버 유사문서에 걸리지 않게 흔한 보호소 홍보 문장과 다른 표현을 쓰세요.

필드:
- meta_description: 120자 안팎, 입양과 파양 상담을 모두 언급
- hero_eyebrow: 짧은 한 줄
- hero_headline: 3개 문자열 (줄바꿈용)
- hero_lede: 2문장, 입양은 {ADOPT_PHONE}로 문의
- waiting_title, waiting_sub
- adopt_steps_title, adopt_steps_sub
- adopt_steps: 3개 {{title, body}}

출력 형식은 위 필드만 가진 JSON 객체 하나입니다.
""".strip()


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing")
    body = {
        "contents": [{"role": "user", "parts": [{"text": PROMPT}]}],
        "generationConfig": {"temperature": 0.85, "responseMimeType": "application/json"},
    }
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
    text = payload["candidates"][0]["content"]["parts"][0]["text"]
    data = json.loads(text[text.find("{") : text.rfind("}") + 1])
    DEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", DEST.name)


if __name__ == "__main__":
    main()
