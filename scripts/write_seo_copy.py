"""Ask Gemini for SEO paragraph banks and long-form guide blocks."""
import json
import os
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
DEST = ROOT / "data" / "seo_copy.json"
MODEL = "gemini-3.8-flash"
ADOPT_PHONE = "0505-464-1004"
INTAKE_PHONE = "0505-707-0401"

PROMPT = f"""
강아지보호소 품으로 지역 SEO 안내용 JSON만 작성하세요. 설명 문장은 쓰지 마세요.
보호소는 전국 전화 상담입니다. 지역마다 지점 주소, 고정 수수료, 당일 입소, 0원 분양가는 만들지 마세요.
{ADOPT_PHONE}는 입양 문의, {INTAKE_PHONE}는 파양·입소 상담입니다.
다음 단어는 절대 쓰지 마세요: 기부, 후원, 봉사, 봉사활동, 안락사, 안락사없는.
무료분양은 판매나 0원 거래처럼 쓰지 말고, 상담 뒤 만나는 입양 절차로 쓰세요.
자리가 없으면 맡길 수 없다고 분명히 쓰세요.
네이버 유사문서를 피하려고 문장 길이와 어순, 예시를 서로 다르게 만드세요.

자리표시는 반드시 이 글자만: {{지역}} {{키워드}} {{동물}} {{전화}}
{{키워드}}는 한 단락에 한 번만.

키는 surrender, shelter, adopt 세 개입니다. 각 키마다:
- p1,p2,p3,p4: 각각 서로 다른 문자열 6개, 각 2~3문장
- region_hooks: {{지역}}만 넣는 지역 생활 맥락 문장 10개 (주소·역 이름은 만들지 말 것)
- steps: 6개 {{title, lead, body, checks}} — 파양/입소/입양 절차를 단계별로 (title은 STEP 1 형식)
  checks는 확인할 항목 3개 문자열 배열
- faq: 6개 {{q, a}} — 파양 방법, 비용 안내 방식, 서류, 픽업, 입양 공고, 사진만 보고 결정하지 말 것 등
- watch: 주의할 상황 4개 문자열 (선입금 강요, 주소 없이 지점이라고 말하기 등)

surrender는 파양·입양보내기 검색자, shelter는 보호소 검색자, adopt는 무료분양·입양 검색자에게 맞게 쓰세요.
adopt의 p2와 faq에서는 {{전화}}에 입양 문의 번호가 들어가게 쓰세요.
surrender와 shelter는 입소 상담 번호가 {{전화}}로 들어가게 쓰세요.
""".strip()

BANNED = ("기부", "후원", "봉사", "안락사")


def scrub(value):
    if isinstance(value, str):
        for word in BANNED:
            if word in value:
                raise ValueError(f"banned word in copy: {word}")
        return value
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items()}
    return value


def main() -> None:
    force = "--force" in sys.argv
    if DEST.exists() and not force:
        print("exists", DEST.name)
        return
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing")
    body = {
        "contents": [{"role": "user", "parts": [{"text": PROMPT}]}],
        "generationConfig": {"temperature": 0.75, "responseMimeType": "application/json"},
    }
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        payload = json.load(response)
    text = payload["candidates"][0]["content"]["parts"][0]["text"]
    data = json.loads(text[text.find("{") : text.rfind("}") + 1])
    data = scrub(data)
    DEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", DEST.name)


if __name__ == "__main__":
    main()
