"""Build the 강아지보호소 품으로 shelter site from the exported pet catalog."""
import hashlib
import html
import json
import pathlib
import random
from datetime import datetime, timedelta, timezone

from comment_bank import AUTHORS
from story_comments import STORY_COMMENTS, STORY_NAMES

KST = timezone(timedelta(hours=9))

ROOT = pathlib.Path(r"f:\강아지보호소품으로")
SITE = ROOT / "site"
PETS_PATH = ROOT / "data" / "pets.json"
BLURBS_PATH = ROOT / "data" / "blurbs.json"
REHOME_PATH = ROOT / "data" / "rehome.json"
STORIES_PATH = ROOT / "data" / "stories.json"
REHOME_IMAGE_DIR = SITE / "assets" / "rehome"

PHONE = "0505-707-0401"
TEL = "05057070401"
ADOPT_PHONE = "0505-464-1004"
ADOPT_TEL = "05054641004"
HOME_COPY_PATH = ROOT / "data" / "home_copy.json"
PHOTO_SHUFFLE_SALT = 0x20261024
LIST_SHUFFLE_SALT = 0xA7C3E91
AREAS = [
    ("서울", "seoul", "아파트 이사나 층간소음, 임대 조건 때문에 더 키우기 어려워졌다는 상담이 많습니다."),
    ("인천", "incheon", "직장과 이사가 겹치며 파양을 고민하는 경우가 있고, 섬 지역은 이동 일정을 상담 때 같이 정합니다."),
    ("경기도", "gyeonggi", "도시와 외곽 모두 같은 전화로 상담합니다. 거리가 멀어도 번호는 다르지 않습니다."),
    ("강원도", "gangwon", "이동 거리가 긴 편이라, 지역과 아이 상태를 먼저 듣고 방문이나 픽업이 가능한지 안내합니다."),
    ("충청도", "chungcheong", "대전, 세종과 생활권이 이어진 상담이 많습니다. 대전·세종은 따로 안내하고, 그 밖의 충청 지역은 이 페이지에서 받습니다."),
    ("대전", "daejeon", "세종, 충청과 가까운 곳에서 오는 상담이 많습니다. 입소 가능 여부는 자리와 아이 상태를 듣고 정합니다."),
    ("세종", "sejong", "이사로 집을 옮기며 강아지를 데려가기 어려워졌다는 상담을 전화로 받습니다."),
    ("전라도", "jeolla", "광주와 생활권이 겹치는 경우가 있습니다. 광주는 별도 페이지에서 안내하고, 그 밖의 전라도는 이 페이지에서 받습니다."),
    ("광주", "gwangju", "전라도 페이지와 나누어, 광주에서 파양을 고민하는 보호자 상담을 따로 안내합니다."),
    ("경상도", "gyeongsang", "부산, 대구, 울산은 각각 별도 페이지가 있습니다. 그 밖의 경상도 지역은 이 페이지에서 상담합니다."),
    ("부산", "busan", "부산에서 키우던 아이의 파양 상담을 전화로 받습니다. 입소가 확정된 뒤에 사진과 입양 공고를 준비합니다."),
    ("대구", "daegu", "대구에서 오는 파양 상담도 전국과 같은 번호로 받습니다. 아이 나이와 건강, 지금 상황을 먼저 듣습니다."),
    ("울산", "ulsan", "울산에서 키우기 어려워진 이유를 듣고, 입소가 가능한 자리인지 전화로 확인합니다."),
    ("제주도", "jeju", "비행이나 배편으로 이동해야 해서, 상담 때 일정과 아이 상태를 먼저 확인합니다."),
]
REGIONS = [name for name, _slug, _note in AREAS]
SITE_ORIGIN = "https://www.naverzine.co.kr"

GENDER = {
    "male": ("남", "남아"),
    "female": ("여", "여아"),
    "unknown": ("미상", "미상"),
}
NEUTER = {"yes": "완료", "no": "안 함", "unknown": "확인 중"}
STATUS = {
    "waiting": ("입양 대기", "pill-waiting", "0"),
    "adopted": ("입양 완료", "pill-adopted", "1"),
}


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


MARK = {
    "c": "mark-color",
    "b": "mark-big",
    "u": "mark-line",
}


def rich_inline(text: str) -> str:
    parts = []
    cursor = 0
    while True:
        start = text.find("{", cursor)
        if start < 0:
            parts.append(esc(text[cursor:]))
            break
        end_tag = text.find("}", start)
        if end_tag < 0 or end_tag - start != 2:
            parts.append(esc(text[cursor : start + 1]))
            cursor = start + 1
            continue
        kind = text[start + 1 : end_tag]
        close = "{" + "/" + kind + "}"
        finish = text.find(close, end_tag)
        if kind not in MARK or finish < 0:
            parts.append(esc(text[cursor : start + 1]))
            cursor = start + 1
            continue
        parts.append(esc(text[cursor:start]))
        inner = text[end_tag + 1 : finish]
        parts.append(f'<span class="{MARK[kind]}">{esc(inner)}</span>')
        cursor = finish + len(close)
    return "".join(parts)


def rich_block(text: str) -> str:
    lines = []
    for line in text.split("\n"):
        if not line.strip():
            lines.append('<span class="gap"></span>')
        else:
            lines.append(f"<span>{rich_inline(line)}</span>")
    return "".join(lines)


def photo_list(pet: dict) -> list[str]:
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
    local = []
    for index, _url in enumerate(urls):
        rel = f"photos/{pet['_id']}/{index}.jpg"
        if (SITE / rel).exists() and (SITE / rel).stat().st_size > 0:
            local.append(rel)
    if len(local) > 1:
        rng = random.Random(int(hashlib.sha256(f"{PHOTO_SHUFFLE_SALT}:{pet['_id']}".encode()).hexdigest()[:8], 16))
        rng.shuffle(local)
    return local


def normalize(pet: dict, blurbs: dict[str, str]) -> dict:
    gender_short, gender_long = GENDER.get(pet.get("gender"), ("미상", "미상"))
    created_at = datetime.fromisoformat(pet["_createdAt"].replace("Z", "+00:00")).astimezone(KST)
    traits = [t for t in (pet.get("traits") or []) if t]
    return {
        "id": pet["_id"],
        "name": pet.get("name") or "이름 미정",
        "species": pet.get("species") or "믹스",
        "age": pet.get("age") or "확인 중",
        "gender_short": gender_short,
        "gender": gender_long,
        "health": pet.get("healthStatus") or "확인 중",
        "neutered": NEUTER.get(pet.get("neutered"), "확인 중"),
        "intake": pet.get("intakeRoute") or "확인 중",
        "created": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        "traits": traits,
        "blurb": blurbs.get(pet["_id"], ""),
        "photos": photo_list(pet),
    }


def head(
    title: str,
    depth: str,
    description: str,
    canonical: str = "",
    image: str = "",
    json_ld: str = "",
) -> str:
    canon = f'\n  <link rel="canonical" href="{esc(canonical)}">' if canonical else ""
    social = ""
    if image:
        social = f"""
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="강아지보호소 품으로">
  <meta property="og:locale" content="ko_KR">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(image)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(image)}">"""
    linked = f'\n  <script type="application/ld+json">{json_ld}</script>' if json_ld else ""
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">{canon}{social}{linked}
  <link rel="icon" href="{depth}assets/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="{depth}assets/favicon.png" type="image/png" sizes="64x64">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Song+Myung&amp;display=swap">
  <link rel="stylesheet" href="{depth}assets/css/site.css">
</head>
<body>
"""


HEART = """<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 20.5s-6.6-4.1-6.6-8.6A3.7 3.7 0 0 1 12 9a3.7 3.7 0 0 1 6.6 2.9c0 4.5-6.6 8.6-6.6 8.6z"/></svg>"""
BUBBLE = """<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5 4.5h14a2 2 0 0 1 2 2v7.5a2 2 0 0 1-2 2H9.2L5 19.8V4.5z"/></svg>"""
_SOCIAL = {}


def _unique(lines: list[str]) -> list[str]:
    seen = set()
    unique = []
    for line in lines:
        text = " ".join((line or "").split())
        if text and text not in seen:
            seen.add(text)
            unique.append(text)
    return unique


def _iro(word: str) -> str:
    last = word[-1] if word else ""
    code = ord(last) if last else 0
    if 0xAC00 <= code <= 0xD7A3 and (code - 0xAC00) % 28:
        return "이라고"
    return "라고"


def _healthy(health: str) -> bool:
    compact = health.replace(" ", "")
    return compact in {"건강함", "건강합", "간강함", "건강합니다"}


def pet_comment_lines(pet: dict) -> list[str]:
    name = pet["name"]
    species = pet["species"]
    age = pet["age"]
    gender = pet["gender"]
    health = (pet.get("health") or "").strip()
    traits = [trait.strip() for trait in pet.get("traits") or [] if trait and trait.strip()]
    blurb = (pet.get("blurb") or "").strip()
    known_age = age and "확인" not in age
    lines = [
        f"{species} {name}, 사진이 소개글이랑 같아요.",
        f"글에 적힌 {species} 얼굴이 사진에 그대로 있어요.",
        f"{name} 사진만 봐도 {species} 소개가 과장이 아니에요.",
        f"좋은 가족이 {name}의 {species}다운 점을 그대로 아껴 주면 좋겠어요.",
    ]
    if known_age:
        lines.append(f"{age} {name}{_iro(name)} 하니, 사진 속 표정이 그 나이로 보여요.")
    if gender in {"남아", "여아"}:
        lines.append(f"{name}, {gender}라는 소개가 사진이랑 어울려요.")
        if known_age:
            lines.append(f"나이 {age}, {gender}, 품종 {species}. 이 세 가지가 사진이랑 같이 보여요.")
    for trait in traits:
        lines.append(f"특징에 「{trait}」{_iro(trait)} 있는데, 사진을 보니 고개가 끄덕여져요.")
        lines.append(f"{name}, 다시 보게 된 이유는 「{trait}」이었어요.")
        lines.append(f"「{trait}」. 이 한 줄이 사진이랑 제일 잘 맞아요.")
    if traits:
        lines.append(f"{species} {name}의 「{traits[0]}」, 사진에서 먼저 느껴졌어요.")
        if len(traits) > 1:
            joined = "」, 「".join(traits)
            lines.append(f"적힌 특징이 「{joined}」인데, 사진이랑 안 어긋나지 않아요.")
    if health and "확인" not in health:
        if _healthy(health):
            lines.append(f"건강하다는 안내를 읽고 나니 {name} 사진이 더 반가워요.")
            lines.append(f"{name}, 건강함이라고 적힌 기본 정보가 사진이랑 잘 맞아요.")
        else:
            lines.append(f"건강 상태에 「{health}」라고 적혀 있어서, 사진을 더 찬찬히 봤어요.")
            lines.append(f"만나기 전에 알고 싶었던 {name} 소식이 「{health}」였어요.")
    if pet.get("neutered") == "완료":
        lines.append(f"{name}, 중성화까지 되어 있다는 안내가 마음에 놓여요.")
    elif pet.get("neutered") == "안 함":
        lines.append("중성화는 아직 안 했다는 기본 정보도 같이 읽어 봤어요.")
    if pet.get("intake") == "구조":
        lines.append(f"구조로 들어온 {name}. 사진이 더 소중해 보여요.")
    elif pet.get("intake") == "파양":
        lines.append(f"파양으로 입소한 {name}. 다음 가족이 이 성격을 알아봐 주면 좋겠어요.")
    elif pet.get("intake") and "확인" not in pet["intake"]:
        lines.append(f"입소 경로는 {pet['intake']}라고 안내되어 있네요.")
    for sentence in blurb.replace("!", ".").replace("?", ".").split("."):
        sentence = sentence.strip()
        if 12 <= len(sentence) <= 90:
            lines.append(f"소개글 그대로예요. {sentence}.")
    return lines


def story_comment_lines(story: dict) -> list[str]:
    written = STORY_COMMENTS.get(str(story["id"])) or []
    if written:
        return written
    lines = [f"「{story['title']}」, 사진이 이 제목이랑 같아요."]
    for block in story.get("blocks") or []:
        if block.get("type") != "text":
            continue
        for line in block.get("lines") or []:
            text = line.strip()
            if len(text) >= 8 and not text.startswith("0505"):
                lines.append(f"글에 적힌 대로예요. {text}")
    return lines


WISHES = [
    "좋은 가족 만나길.",
    "빨리 좋은 가족 만나면 좋겠어요.",
    "좋은 가족만 만나자.",
    "건강히 잘 자라라.",
    "아프지 말고 잘 자라라.",
    "아프지 말고, 밥 잘 먹고, 잘 자라.",
    "따뜻한 집에서 오래오래 사랑받길.",
    "기다리는 시간이 짧았으면 좋겠어요.",
    "꼭 좋은 데로 가세요.",
    "사랑받을 일만 남았으면 해요.",
    "건강한 모습 그대로 가족 만나길.",
    "지금처럼 건강하고, 그다음은 좋은 가족이 이어 주길.",
    "외롭지 않게, 좋은 손에서 자라길.",
    "좋은 가족, 맛있는 밥, 포근한 잠자리 만나길.",
    "댓글로나마 쓰다듬고 갑니다. 잘 자라.",
    "어디 아프지 말고 편히 지내.",
    "좋은 인연이 빨리 나타났으면.",
    "사진 보는 동안에도 좋은 가족이 생기길 빌었어요.",
    "남은 날들 건강하게, 그리고 행복하게.",
    "가족 되는 날이 하루라도 빨리 오면 좋겠어요.",
]


def wish_lines(name: str) -> list[str]:
    lines = list(WISHES)
    if name:
        lines.extend(
            [
                f"{name}, 좋은 가족 만나.",
                f"{name}, 빨리 좋은 가족 만나면 좋겠어요.",
                f"{name}, 건강히 잘 자라라.",
                f"{name}, 아프지 말고 잘 자라.",
                f"{name}, 따뜻한 집에서 오래 사랑받길.",
                f"{name}, 좋은 사람만 만나자.",
                f"{name}도 아프지 말고 무럭무럭.",
                f"{name}, 기다리는 동안도 건강히.",
            ]
        )
    return lines


def _weave(content: list[str], wishes: list[str]) -> list[str]:
    if not wishes:
        return content
    if not content:
        return wishes
    merged = []
    step = max(1, len(content) // len(wishes))
    cursor = 0
    for wish in wishes:
        merged.extend(content[cursor : cursor + step])
        cursor += step
        merged.append(wish)
    merged.extend(content[cursor:])
    return merged


def engagement(key: str, lines: list[str], name: str = "") -> dict:
    cached = _SOCIAL.get(key)
    if cached:
        return cached
    seed = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:12], 16)
    rng = random.Random(seed)
    content = _unique(lines)
    wishes = _unique(wish_lines(name))
    count = rng.randint(15, 30)
    wish_count = min(len(wishes), max(5, round(count * 0.35)))
    content_count = min(len(content), max(0, count - wish_count))
    while content_count + wish_count < 15 and wish_count < len(wishes):
        wish_count += 1
    picked_content = rng.sample(content, content_count) if content_count else []
    picked_wishes = rng.sample(wishes, wish_count) if wish_count else []
    picked = _weave(picked_content, picked_wishes)
    authors = AUTHORS[:]
    rng.shuffle(authors)
    comments = [{"name": authors[index], "text": text} for index, text in enumerate(picked)]
    data = {"likes": rng.randint(80, 140), "comments": comments}
    _SOCIAL[key] = data
    return data


def react_row(data: dict) -> str:
    return (
        f'<div class="react"><span>{HEART}{data["likes"]}</span>'
        f'<span>{BUBBLE}{len(data["comments"])}</span></div>'
    )


def comment_section(data: dict) -> str:
    items = "".join(
        f'<li><strong>{esc(item["name"])}</strong><p>{esc(item["text"])}</p></li>'
        for item in data["comments"]
    )
    return f"""<section class="comment-box">
  <h2>댓글 {len(data["comments"])}</h2>
  <div class="react react-detail"><span>{HEART}좋아요 {data["likes"]}</span><span>{BUBBLE}댓글 {len(data["comments"])}</span></div>
  <ul>{items}</ul>
</section>
"""


def nav(depth: str, current: str) -> str:
    def item(href: str, label: str, key: str) -> str:
        current_attr = ' aria-current="page"' if key and current == key else ""
        return f'<a href="{depth}{href}"{current_attr}>{label}</a>'

    return f"""<header class="nav">
  <div class="nav-inner">
    <a class="brand" href="{depth}index.html">
      <img class="logo" src="{depth}assets/logo.jpg" alt="강아지보호소 품으로" width="54" height="54" loading="eager">
      <span><span class="brand-name">강아지보호소</span><span class="brand-sub">품으로</span></span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-label="메뉴 열기">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav-links" id="site-nav">
      {item("index.html", "홈", "home")}
      {item("pets/index.html", "입양하기", "pets")}
      {item("index.html#rehome", "파양 입소", "")}
      {item("index.html#story", "이렇게 지내요", "story")}
    </nav>
  </div>
</header>
<script>
const navToggle = document.querySelector(".nav-toggle");
const navLinks = document.querySelector(".nav-links");
if (navToggle && navLinks) {{
  navToggle.addEventListener("click", () => {{
    const open = navLinks.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    navToggle.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
  }});
  navLinks.querySelectorAll("a").forEach((link) => {{
    link.addEventListener("click", () => {{
      navLinks.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
      navToggle.setAttribute("aria-label", "메뉴 열기");
    }});
  }});
}}
</script>
"""


PHONE_ICON = """<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.7 10.8c.9 1.7 2.2 3.2 3.9 4.3l2-2c.3-.3.8-.4 1.2-.3 1.1.4 2.3.6 3.5.6.6 0 1 .4 1 1V19c0 .6-.4 1-1 1C10.6 20 4 13.4 4 5c0-.6.4-1 1-1h4.6c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.5.1.4 0 .9-.3 1.2l-2 2z"/></svg>"""


def callbar() -> str:
    return f"""<div class="callbar">
  <a class="call-adopt" href="tel:{ADOPT_TEL}">{PHONE_ICON}<span>강아지입양<small>{ADOPT_PHONE}</small></span></a>
  <a class="call-rehome" href="tel:{TEL}">{PHONE_ICON}<span>강아지파양입소<small>{PHONE}</small></span></a>
</div>
"""


def footer(depth: str) -> str:
    return f"""<footer>
  <div class="wrap">© 2026 강아지보호소 품으로</div>
</footer>
{callbar()}</body>
</html>
"""


def card(pet: dict, depth: str) -> str:
    photo = pet["photos"][0] if pet["photos"] else ""
    img = (
        f'<img src="{depth}{esc(photo)}" alt="{esc(pet["name"])}" loading="lazy">'
        if photo
        else ""
    )
    traits = "".join(f'<span class="trait">{esc(trait)}</span>' for trait in pet["traits"][:3])
    search = " ".join(
        [pet["name"], pet["species"], pet["age"], pet["gender"], *pet["traits"]]
    ).lower()
    social = engagement(pet["id"], pet_comment_lines(pet), pet["name"])
    return f"""<article class="card" data-pet data-name="{esc(pet["name"])}" data-search="{esc(search)}">
  <a href="{depth}pets/{esc(pet["id"])}/index.html">
    <div class="card-photo">{img}</div>
    <div class="card-body">
      <h3>{esc(pet["name"])}</h3>
      <div class="meta">{esc(pet["species"])} · {esc(pet["age"])} · {esc(pet["gender_short"])}</div>
      <div class="traits">{traits}</div>
      {react_row(social)}
    </div>
  </a>
</article>
"""


def write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


REASON_FALLBACK = [
    ("임신, 출산", "reason-01", "출산 전후로\n돌보기 어렵거나\n\n아기와 함께 두기\n{c}불안할 때{/c}"),
    ("알러지", "reason-02", "함께 살다\n{c}동물 알러지{/c}가 나타나\n생활이 어려워졌을 때"),
    ("이사, 이민, 유학", "reason-03", "해외로 데려갈 수 없거나\n이사한 집에서\n함께하기 어려울 때\n\n군 입대와 오랜 부재도\n같은 경우에 가깝습니다."),
    ("나이 든 보호자와 아이", "reason-04", "보호자가 아프거나\n연로해졌을 때\n\n아이도 나이가 들어\n집에서 돌보기 어려울 때"),
]
REASON_ALIAS = {
    "이민": 2,
    "군 입대": 2,
    "알러지": 1,
    "보호자 부재": 3,
    "임신": 0,
    "출산": 0,
}


def rehome_section(depth: str = "") -> str:
    if not REHOME_PATH.exists():
        return ""
    data = json.loads(REHOME_PATH.read_text(encoding="utf-8"))
    intro_html = "".join(f'<p class="rehome-lede">{esc(part)}</p>' for part in data.get("intro") or [])
    reason_cards = []
    reasons_raw = data.get("reasons") or []
    reason_rows = (
        list(REASON_FALLBACK)
        if reasons_raw and all(isinstance(item, str) for item in reasons_raw)
        else reasons_raw
    )
    for reason in reason_rows:
        if isinstance(reason, tuple):
            title, stem, body = reason
            image = ""
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                candidate = REHOME_IMAGE_DIR / f"{stem}{ext}"
                if candidate.exists():
                    image = f"{depth}assets/rehome/{stem}{ext}"
                    break
            photo = f'<img src="{esc(image)}" alt="">' if image else ""
            reason_cards.append(
                f"""<article class="reason-card">
  {photo}
  <div>
    <h3>{esc(title)}</h3>
    <p class="soft">{rich_block(body)}</p>
  </div>
</article>"""
            )
            continue
        if isinstance(reason, str):
            index = REASON_ALIAS.get(reason.strip(), len(reason_cards) % len(REASON_FALLBACK))
            title, stem, body = REASON_FALLBACK[index]
            image = ""
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                candidate = REHOME_IMAGE_DIR / f"{stem}{ext}"
                if candidate.exists():
                    image = f"{depth}assets/rehome/{stem}{ext}"
                    break
            photo = f'<img src="{esc(image)}" alt="">' if image else ""
            reason_cards.append(
                f"""<article class="reason-card">
  {photo}
  <div>
    <h3>{esc(title)}</h3>
    <p class="soft">{rich_block(body)}</p>
  </div>
</article>"""
            )
            continue
        image = ""
        stem = reason.get("image") or ""
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidate = REHOME_IMAGE_DIR / f"{stem}{ext}"
            if stem and candidate.exists():
                image = f"{depth}assets/rehome/{stem}{ext}"
                break
        photo = f'<img src="{esc(image)}" alt="">' if image else ""
        reason_cards.append(
            f"""<article class="reason-card">
  {photo}
  <div>
    <h3>{esc(reason.get("title") or "")}</h3>
    <p class="soft">{rich_block(reason.get("body") or "")}</p>
  </div>
</article>"""
        )
    default_cases = [
        "임신, 출산으로\n돌보기 어려울 때",
        "알러지가 생겨\n함께 지내기 힘들 때",
        "이민, 유학, 군 입대로\n돌볼 사람이 없을 때",
        "이사를 해도\n아이를 데려갈 수 없을 때",
        "보호자가 아프거나\n연로해졌을 때",
        "아이도 나이가 들어\n집에서 돌보기 어려울 때",
    ]
    cases = "".join(
        f"<li>{rich_block(item)}</li>" for item in (data.get("cases") or default_cases)
    )
    quote_lines = []
    for line in data.get("quote_lines") or []:
        quote_lines.append(f'<span class="q-{esc(line.get("size") or "md")}">{esc(line.get("text") or "")}</span>')
    if not quote_lines and data.get("quote"):
        quote = data["quote"].strip()
        if "마지막 선물" in quote:
            preset = [
                ("새로운 가족을 찾아 주는 일은", "md"),
                ("아이에게 건넬 수 있는", "sm"),
                ("마지막 선물입니다.", "lg"),
            ]
            quote_lines = [f'<span class="q-{size}">{esc(text)}</span>' for text, size in preset]
        else:
            quote_lines.append(f'<span class="q-lg">{esc(quote)}</span>')
    steps = []
    for index, step in enumerate(data.get("steps") or [], start=1):
        image = ""
        stem = f"{index:02d}"
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            candidate = REHOME_IMAGE_DIR / f"{stem}{ext}"
            if candidate.exists():
                image = f"{depth}assets/rehome/{stem}{ext}"
                break
        img = f'<img src="{esc(image)}" alt="{esc(step.get("title") or "")}">' if image else ""
        steps.append(
            f"""<article class="rehome-step">
  <div class="rehome-photo">{img}</div>
  <div class="rehome-copy">
    <em>{index:02d}</em>
    <h3>{esc(step.get("title") or "")}</h3>
    <p class="soft">{rich_block(step.get("body") or "")}</p>
  </div>
</article>"""
        )
    return f"""<section class="section" id="rehome">
  <div class="wrap">
    <div class="rehome-intro">
      <p class="eyebrow">REHOMING</p>
      <h2>{esc(data.get("title") or "강아지 파양 입소")}</h2>
      {intro_html}
    </div>
    <blockquote class="rehome-quote">{"".join(quote_lines)}</blockquote>
    <div class="reason-grid">
      {"".join(reason_cards)}
    </div>
    <div class="case-box">
      <h3>이럴 때 입소를 알아봅니다</h3>
      <ul>{cases}</ul>
    </div>
    <div class="section-head rehome-process-head">
      <div>
        <h2>입소 절차</h2>
        <p>상담부터 입양 공고까지, 순서는 같습니다.</p>
      </div>
    </div>
    <div class="rehome-steps">
      {"".join(steps)}
    </div>
  </div>
</section>
"""


def load_stories() -> list[dict]:
    if not STORIES_PATH.exists():
        return []
    stories = json.loads(STORIES_PATH.read_text(encoding="utf-8"))
    return [story for story in stories if story.get("title") and story.get("cover")]


def story_card(story: dict, depth: str) -> str:
    social = engagement("story-" + story["id"], story_comment_lines(story), STORY_NAMES.get(str(story["id"]), ""))
    return f"""<a class="story-card" href="{depth}stories/{esc(story["id"])}/index.html">
  <div class="story-photo"><img src="{depth}{esc(story["cover"])}" alt="" loading="lazy"></div>
  <div class="story-body">
    <h3>{esc(story["title"])}</h3>
    {react_row(social)}
  </div>
</a>
"""


def story_section(stories: list[dict], depth: str) -> str:
    if not stories:
        return ""
    cards = "".join(story_card(story, depth) for story in stories)
    return f"""<section class="section" id="story">
  <div class="wrap">
    <div class="section-head">
      <div>
        <h2>아이들은 이렇게 지내요</h2>
        <p>산책하고, 밥 먹고, 미용하는 보호소의 하루입니다. 사진을 누르면 그 이야기를 볼 수 있어요.</p>
      </div>
    </div>
    <div class="story-grid">{cards}</div>
  </div>
</section>
"""


def scrub_story_line(line: str) -> str:
    return (
        line.replace("0505-300-7779", ADOPT_PHONE)
        .replace("05053007779", ADOPT_TEL)
    )


def story_body(story: dict, depth: str) -> str:
    parts = []
    story_seed = int(hashlib.sha256(f"story:{story.get('id')}".encode()).hexdigest()[:8], 16)
    for block in story.get("blocks") or []:
        if block.get("type") == "text":
            lines = "".join(
                f"<span>{esc(scrub_story_line(line))}</span>" for line in block.get("lines") or []
            )
            if lines:
                parts.append(f'<div class="story-text">{lines}</div>')
        elif block.get("type") == "images":
            files = list(block.get("files") or [])
            if len(files) > 1:
                rng = random.Random(story_seed ^ PHOTO_SHUFFLE_SALT)
                rng.shuffle(files)
            imgs = "".join(
                f'<img src="{depth}{esc(path)}" alt="{esc(story["title"])}" loading="lazy">'
                for path in files
            )
            single = " single" if len(files) == 1 else ""
            if imgs:
                parts.append(f'<div class="story-photos{single}">{imgs}</div>')
        elif block.get("type") == "video" and block.get("file"):
            poster = block.get("poster") or ""
            poster_attr = f' poster="{depth}{esc(poster)}"' if poster else ""
            caption = f'<p class="story-caption">{esc(block.get("caption") or "")}</p>' if block.get("caption") else ""
            parts.append(
                f'<figure class="story-video">{caption}<video controls playsinline preload="metadata"{poster_attr}>'
                f'<source src="{depth}{esc(block["file"])}" type="video/mp4"></video></figure>'
            )
    return "".join(parts)


def build_stories(stories: list[dict]) -> None:
    for story in stories:
        page = head(
            f"{story['title']} — 강아지보호소 품으로",
            "../../",
            story["title"],
        )
        page += nav("../../", "story")
        social = engagement("story-" + story["id"], story_comment_lines(story), STORY_NAMES.get(str(story["id"]), ""))
        page += f"""<main class="wrap story-page">
  <a class="crumb" href="../../index.html#story">← 아이들은 이렇게 지내요</a>
  <h1>{esc(story["title"])}</h1>
  {story_body(story, "../../")}
  {comment_section(social)}
</main>
"""
        page += footer("../../")
        write(SITE / "stories" / story["id"] / "index.html", page)


ADOPT_MARK = """<span class="call-ico" aria-hidden="true"><svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 20.6s-6.8-4.2-6.8-8.8A3.8 3.8 0 0 1 12 8.6a3.8 3.8 0 0 1 6.8 3.2c0 4.6-6.8 8.8-6.8 8.8z"/></svg></span>"""
INTAKE_MARK = """<span class="call-ico" aria-hidden="true"><span class="ring"></span><span class="ring delay"></span><svg viewBox="0 0 24 24"><path fill="currentColor" d="M6.7 10.8c.9 1.7 2.2 3.2 3.9 4.3l2-2c.3-.3.8-.4 1.2-.3 1.1.4 2.3.6 3.5.6.6 0 1 .4 1 1V19c0 .6-.4 1-1 1C10.6 20 4 13.4 4 5c0-.6.4-1 1-1h4.6c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.5.1.4 0 .9-.3 1.2l-2 2z"/></svg></span>"""


def contact_section() -> str:
    regions = "".join(f"<li>{esc(name)}</li>" for name in REGIONS)
    return f"""<section id="contact">
  <div class="wrap">
    <div class="contact-band">
      <div class="contact-copy">
        <p class="eyebrow">CONTACT</p>
        <h2>전국 통합문의</h2>
        <p>입양과 입소, 전국 어디서든 전화로 상담합니다.</p>
      </div>
      <div class="contact-phones">
        <a class="contact-call adopt" href="tel:{ADOPT_TEL}">{ADOPT_MARK}<span class="call-copy"><small>입양 상담</small><strong>{ADOPT_PHONE}</strong></span></a>
        <a class="contact-call rehome" href="tel:{TEL}">{INTAKE_MARK}<span class="call-copy"><small>입소 상담</small><strong>{PHONE}</strong></span></a>
      </div>
      <div class="region-block">
        <p>전국 입소문의</p>
        <ul class="regions">{regions}</ul>
      </div>
    </div>
  </div>
</section>
"""


def place_directory_section(depth: str) -> str:
    from seo_places import PLACES

    links = "".join(f'<a href="{depth}k/{esc(name)}/">{esc(name)}</a>' for name in PLACES)
    return f"""<section class="section" id="areas">
  <div class="wrap">
    <details class="seo-fold">
      <summary aria-label="지역별 안내">
        <span class="seo-toggle"></span>
      </summary>
      <div class="section-head">
        <div>
          <h2>지역별 안내</h2>
          <p>사는 곳을 누르면 강아지파양, 보호소, 입양 안내로 이어집니다. 상담은 전국 전화로 받습니다.</p>
        </div>
      </div>
      <div class="place-links">{links}</div>
    </details>
  </div>
</section>
"""


def write_webdoc_txt(urls: list[str], chunk_size: int = 2000) -> None:
    folder = ROOT / "웹문서등록"
    folder.mkdir(exist_ok=True)
    for old in folder.glob("*.txt"):
        old.unlink()
    if not urls:
        return
    for index in range(0, len(urls), chunk_size):
        batch = urls[index : index + chunk_size]
        start = index + 1
        end = index + len(batch)
        part = index // chunk_size + 1
        name = f"{part:02d}-{start:04d}-{end:04d}.txt"
        (folder / name).write_text("\n".join(batch) + "\n", encoding="utf-8")


def write_sitemap(pets: list[dict], stories: list[dict], extras: list[str] | None = None) -> None:
    urls = [f"{SITE_ORIGIN}/", f"{SITE_ORIGIN}/pets/", f"{SITE_ORIGIN}/k/"]
    urls.extend(extras or [])
    urls.extend(f"{SITE_ORIGIN}/stories/{story['id']}/" for story in stories)
    urls.extend(f"{SITE_ORIGIN}/pets/{pet['id']}/" for pet in pets)
    urls = list(dict.fromkeys(urls))
    body = "".join(f"  <url><loc>{esc(url)}</loc></url>\n" for url in urls)
    write(SITE / "sitemap.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}</urlset>
""")
    write(SITE / "robots.txt", f"""User-agent: *
Allow: /

Sitemap: {SITE_ORIGIN}/sitemap.xml
""")


def load_home_copy() -> dict:
    if not HOME_COPY_PATH.exists():
        return {}
    return json.loads(HOME_COPY_PATH.read_text(encoding="utf-8"))


def front_body(pets: list[dict], stories: list[dict], depth: str, headline_tag: str) -> str:
    home = load_home_copy()
    hero = pets[:3]
    featured = pets[:6]
    hero_html = ""
    for pet in hero:
        photo = f"{depth}{esc(pet['photos'][0])}" if pet["photos"] else ""
        social = engagement(pet["id"], pet_comment_lines(pet), pet["name"])
        hero_html += (
            f'<a href="{depth}pets/{esc(pet["id"])}/index.html">'
            f'<img src="{photo}" alt="{esc(pet["name"])}">'
            f'<div class="hero-meta">'
            f'<span class="hero-name">{esc(pet["name"])}</span>'
            f'<div class="hero-react">{react_row(social)}</div>'
            f'</div></a>'
        )
    cards = "\n".join(card(pet, depth) for pet in featured)
    headline_lines = home.get("hero_headline") or ["오늘도,", "한 아이를", "기다립니다."]
    headline_inner = "<br>".join(esc(line) for line in headline_lines)
    if headline_tag == "h1":
        headline = f"<h1>{headline_inner}</h1>"
    else:
        headline = f'<p class="hero-title">{headline_inner}</p>'
    eyebrow = esc(home.get("hero_eyebrow") or "강아지보호소 품으로")
    lede = esc(
        home.get("hero_lede")
        or "사진과 성격을 보고 마음에 드는 아이를 고르세요. 입양 문의는 전화로 생활 이야기를 나눈 뒤, 예약 방문으로 직접 만납니다."
    )
    waiting_title = esc(home.get("waiting_title") or "가족을 기다리는 아이들")
    waiting_sub = esc(home.get("waiting_sub") or "카드를 누르면 사진과 짧은 소개, 특징을 볼 수 있습니다.")
    adopt_steps = home.get("adopt_steps") or [
        {"title": "전화로 맞춤 안내", "body": f"입양 문의 {ADOPT_PHONE}로 사는 환경과 찾는 성향을 듣고, 만날 수 있는 아이를 소개합니다."},
        {"title": "예약 방문", "body": "보호소는 예약제입니다. 아이와 시간을 보내며 서로의 생활 리듬이 맞는지 살펴봅니다."},
        {"title": "함께하기", "body": "적응 기간을 두고 입양을 확정합니다. 이후에도 생활 적응이 걱정되면 전화로 이야기를 이어갈 수 있습니다."},
    ]
    step_html = "".join(
        f'<article class="step"><em>{index:02d}</em><h3>{esc(row.get("title", ""))}</h3>'
        f'<p>{esc(row.get("body", ""))}</p></article>'
        for index, row in enumerate(adopt_steps[:3], start=1)
    )
    return f"""<section class="hero">
    <div class="wrap hero-grid">
      <div>
        <p class="eyebrow">{eyebrow}</p>
        {headline}
        <p class="lede">{lede}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{depth}pets/index.html">입양 아이들 보기</a>
          <a class="btn btn-ghost" href="tel:{ADOPT_TEL}">입양 문의</a>
        </div>
      </div>
      <div class="hero-photos">{hero_html}</div>
    </div>
  </section>
  {rehome_section(depth)}
  <section class="section" id="waiting">
    <div class="wrap">
      <div class="section-head">
        <div>
          <h2>{waiting_title}</h2>
          <p>{waiting_sub}</p>
        </div>
        <a class="more" href="{depth}pets/index.html">전체 보기</a>
      </div>
      <div class="grid">{cards}</div>
    </div>
  </section>
  <section class="section" id="adopt-steps">
    <div class="wrap">
      <div class="section-head">
        <div>
          <h2>{esc(home.get("adopt_steps_title") or "입양은 이렇게 진행됩니다")}</h2>
          <p>{esc(home.get("adopt_steps_sub") or "급하게 결정하지 않고, 생활이 맞는지 차례대로 확인합니다.")}</p>
        </div>
      </div>
      <div class="steps">
        {step_html}
      </div>
    </div>
  </section>
  {story_section(stories, depth)}"""


def build_home(pets: list[dict], stories: list[dict]) -> None:
    home = load_home_copy()
    page = head(
        "강아지보호소 품으로",
        "",
        home.get("meta_description")
        or "강아지보호소 품으로 입양 안내와 전국 강아지·고양이 파양 입소 상담. 사진으로 아이를 보고 전화로 만남을 정합니다.",
        f"{SITE_ORIGIN}/",
    )
    page += nav("", "home")
    page += f"""<main>
  {front_body(pets, stories, "", "h1")}
  {place_directory_section("")}
  {contact_section()}
</main>
"""
    page += footer("")
    write(SITE / "index.html", page)


def build_board(pets: list[dict]) -> None:
    cards = "\n".join(card(pet, "../") for pet in pets)
    page = head(
        "입양하기 — 강아지보호소 품으로",
        "../",
        "강아지보호소 품으로에서 가족을 기다리는 아이들입니다.",
    )
    page += nav("../", "pets")
    page += f"""<main class="wrap board-hero">
  <p class="eyebrow">ADOPTION</p>
  <h1>입양하기</h1>
  <p class="lede">마음에 드는 아이를 누르면 사진과 짧은 이야기를 볼 수 있어요.</p>
  <div class="grid" id="grid">{cards}</div>
</main>
"""
    page += footer("../")
    write(SITE / "pets" / "index.html", page)


def fact(label: str, value: str) -> str:
    return f'<div class="fact"><span>{esc(label)}</span><strong>{esc(value)}</strong></div>'


def build_detail(pet: dict, others: list[dict]) -> None:
    photos = pet["photos"]
    main = f"../../{photos[0]}" if photos else ""
    main_img = f'<img id="hero-photo" src="{esc(main)}" alt="{esc(pet["name"])}">' if main else ""
    thumbs = ""
    for index, photo in enumerate(photos):
        current = ' aria-current="true"' if index == 0 else ""
        src = f"../../{photo}"
        thumbs += (
            f'<button type="button" data-src="{esc(src)}" data-alt="{esc(pet["name"])} 사진 {index + 1}"{current}>'
            f'<img src="{esc(src)}" alt=""></button>'
        )
    traits = "".join(f'<span class="trait">{esc(trait)}</span>' for trait in pet["traits"])
    related = "\n".join(card(other, "../../") for other in others)
    gallery_script = """
<script>
const hero = document.querySelector("#hero-photo");
document.querySelectorAll(".thumbs button").forEach((button) => {
  button.addEventListener("click", () => {
    if (!hero) return;
    hero.src = button.dataset.src;
    hero.alt = button.dataset.alt;
    document.querySelectorAll(".thumbs button").forEach((item) => item.removeAttribute("aria-current"));
    button.setAttribute("aria-current", "true");
  });
});
</script>
"""
    page = head(
        f"{pet['name']} — 강아지보호소 품으로",
        "../../",
        f"{pet['name']}, {pet['species']}, {pet['age']}, {pet['gender']}. {', '.join(pet['traits'])}",
    )
    page += nav("../../", "")
    page += f"""<main class="wrap detail">
  <a class="crumb" href="../index.html">← 입양 목록</a>
  <div class="detail-grid">
    <div>
      <div class="frame">{main_img}</div>
      <div class="thumbs">{thumbs}</div>
    </div>
    <div class="detail-copy">
      <h1>{esc(pet["name"])}</h1>
      <p class="lede">{esc(pet["species"])} · {esc(pet["age"])} · {esc(pet["gender"])}</p>
      <p class="blurb">{esc(pet["blurb"])}</p>
      <div class="traits">{traits}</div>
      <div class="facts">
        {fact("품종", pet["species"])}
        {fact("나이", pet["age"])}
        {fact("성별", pet["gender"])}
        {fact("건강 상태", pet["health"])}
        {fact("중성화", pet["neutered"])}
        {fact("입소 경로", pet["intake"])}
      </div>
      <div class="detail-actions">
        <a class="btn btn-primary" href="tel:{ADOPT_TEL}">입양 문의 {ADOPT_PHONE}</a>
        <a class="btn btn-ghost" href="../index.html">다른 아이 보기</a>
      </div>
    </div>
  </div>
  {comment_section(engagement(pet["id"], pet_comment_lines(pet), pet["name"]))}
  <section class="section">
    <div class="section-head">
      <div>
        <h2>다른 아이들도 만나보세요</h2>
      </div>
      <a class="more" href="../index.html">전체 보기</a>
    </div>
    <div class="grid">{related}</div>
  </section>
</main>
{gallery_script}
"""
    page += footer("../../")
    write(SITE / "pets" / pet["id"] / "index.html", page)


def main() -> None:
    raw = json.loads(PETS_PATH.read_text(encoding="utf-8"))
    blurbs = json.loads(BLURBS_PATH.read_text(encoding="utf-8")) if BLURBS_PATH.exists() else {}
    public = [normalize(pet, blurbs) for pet in raw if pet.get("status") in STATUS]
    public.sort(key=lambda pet: pet["name"])
    public.sort(key=lambda pet: pet["created"], reverse=True)
    order_rng = random.Random(LIST_SHUFFLE_SALT)
    order_rng.shuffle(public)
    stories = load_stories()
    missing = [pet["name"] for pet in public if not pet["photos"]]
    missing_blurbs = [pet["name"] for pet in public if not pet["blurb"]]
    build_home(public, stories)
    from seo_pages import build_keyword_pages

    extra_urls = build_keyword_pages(public, stories, front_body)
    write_sitemap(public, stories, extra_urls)
    write_webdoc_txt(extra_urls)
    build_stories(stories)
    build_board(public)
    for pet in public:
        others = [other for other in public if other["id"] != pet["id"]][:3]
        build_detail(pet, others)
    catalog = SITE / "data"
    catalog.mkdir(parents=True, exist_ok=True)
    (catalog / "pets.json").write_text(
        json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"pages {len(public)} missing-photos {len(missing)} missing-blurbs {len(missing_blurbs)}")
    if missing:
        print("missing photos", ", ".join(missing))
    if missing_blurbs:
        print("missing blurbs", ", ".join(missing_blurbs))


if __name__ == "__main__":
    main()
