"""Generate five long-form SEO article variants per intent (Gemini)."""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
DEST = ROOT / "data" / "seo_articles.json"
MODEL = "gemini-3.8-flash"
ADOPT_PHONE = "0505-464-1004"
INTAKE_PHONE = "0505-707-0401"

BANNED = ("기부", "후원", "봉사", "안락사")

INTENTS = {
    "surrender": {
        "label": "파양·입양보내기·입소",
        "phone": INTAKE_PHONE,
        "topics": """
강아지 파양 방법, 파양 절차, 파양 비용, 파양 보내는 곳, 입양보내기, 개인 파양 vs 보호소,
픽업 가능 여부, 준비 서류, 동물등록 변경, 중성화·예방접종 기록, 분리불안·입질 등 행동 정보,
당일 입소 가능 여부, 자리 없을 때, 유기하지 않는 선택, 이사·이민·군입대·알러지·출산·질병 사유,
사진만 보고 결정하지 말 것, 선입금·예약금 주의, 입소 후 입양 공고 흐름, 비용은 상담 후 안내(고정가 금지).
""",
    },
    "shelter": {
        "label": "보호소·센터",
        "phone": INTAKE_PHONE,
        "topics": """
유기견보호소·보호센터 차이, 입소 상담, 맡기는 조건, 정원·자리 확인, 건강·격리 관리,
파양과 보호의 경계, 서류·동의, 픽업, 지역명 검색과 전국 상담, 허위 지점 주소 주의,
입소 후 입양 연계, 사진·영상 기록, 비용 안내 방식, 당일 방문, 준비물, 동물등록.
""",
    },
    "adopt": {
        "label": "무료분양·입양",
        "phone": ADOPT_PHONE,
        "topics": """
강아지 무료분양·입양 절차, 입양 문의, 만남 전 상담, 가족·주거 환경 확인, 대면에서 컨디션 보기,
예방접종·구충·사료·배변 습관, 입양 후 적응, 임시 보호, 입양 비용(상담 안내, 판매 아님),
사진·영상만으로 결정하지 말기, 연령·체급·활동량 맞춤, 알레르지 가족 접촉 테스트, 관련 검색 궁금증.
""",
    },
}


def prompt(intent: str) -> str:
    meta = INTENTS[intent]
    return f"""
강아지보호소 품으로 SEO 장문 안내 JSON만 출력하세요. 설명 문장은 쓰지 마세요.
의도: {meta["label"]} 검색자용. 전국 전화 상담, {{지역}} {{키워드}} {{동물}} {{전화}} 자리표시만 사용.
{{키워드}}는 각 단락에 최대 1번. 지역 지점 주소·고정 수수료·0원 거래·당일 무조건 입소 금지.
금지 단어: 기부, 후원, 봉사, 봉사활동, 안락사, 안락사없는.
입양 문의 {ADOPT_PHONE}, 파양·입소 {INTAKE_PHONE}.
네이버 연관검색·궁금증 반영:
{meta["topics"]}

variants 배열 5개. 각 variant는 서로 다른 글쓰기 톤(차분한 설명형, Q&A형, 절차 중심, 체크리스트형, 사례 중심).
각 variant 전체 글자 수(공백 포함) 2200자 이상.
각 variant 구조:
- sections: 8~10개
- section: {{"heading":"소제목(h3 수준)","paragraphs":["2~4문장", ...], "bullets": ["선택 checklist", ...], "subheading": "선택 h4"}}

소제목 예: "STEP 1 · 전화 상담", "파양 비용은 어떻게 안내되나요", "준비 서류", "픽업과 방문", "주의할 상황", "자주 헷갈리는 점" 등.
미유펫 상세페이지처럼 단계·확인사항·FAQ형 소제목을 섞되 문장은 전부 새로 작성(표절 금지).
출력: {{"variants":[...]}} 키 하나만, intent 이름은 넣지 마세요.
""".strip()


def scrub(value):
    if isinstance(value, str):
        for word in BANNED:
            if word in value:
                raise ValueError(f"banned: {word}")
        return value
    if isinstance(value, list):
        return [scrub(v) for v in value]
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items()}
    return value


def call_gemini(text: str, api_key: str) -> dict:
    body = {
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {"temperature": 0.85, "responseMimeType": "application/json"},
    }
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        payload = json.load(response)
    raw = payload["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(raw[raw.find("{") : raw.rfind("}") + 1])


def char_count(variant: dict) -> int:
    total = 0
    for sec in variant.get("sections") or []:
        for p in sec.get("paragraphs") or []:
            total += len(p)
        for b in sec.get("bullets") or []:
            total += len(b)
        total += len(sec.get("heading") or "")
        total += len(sec.get("subheading") or "")
    return total


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is missing")
    only = None
    for arg in sys.argv[1:]:
        if arg.startswith("--intent="):
            only = arg.split("=", 1)[1]
    data = {}
    if DEST.exists() and "--force" not in sys.argv:
        data = json.loads(DEST.read_text(encoding="utf-8"))
    targets = [only] if only else list(INTENTS)
    for intent in targets:
        if intent in data and "--force" not in sys.argv and only is None:
            print("skip", intent)
            continue
        last_error = None
        for attempt in range(2):
            try:
                payload = call_gemini(prompt(intent), api_key)
                variants = payload.get("variants") or payload.get(intent, {}).get("variants")
                if not variants or len(variants) < 5:
                    raise ValueError(f"{intent} variants {len(variants or [])}")
                variants = scrub(variants[:5])
                for index, variant in enumerate(variants):
                    count = char_count(variant)
                    if count < 1800:
                        raise ValueError(f"{intent} v{index} short {count}")
                data[intent] = {"variants": variants}
                DEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"wrote {intent} chars", [char_count(v) for v in variants], flush=True)
                last_error = None
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError, KeyError) as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:400] if isinstance(exc, urllib.error.HTTPError) else str(exc)
                last_error = detail
                print(f"retry {intent} {attempt + 1} {detail}", flush=True)
        if last_error:
            raise SystemExit(last_error)
    print("done", DEST.name)


if __name__ == "__main__":
    main()
