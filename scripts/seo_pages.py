"""Keyword landing pages: full homepage, then a blog above the contact band."""
import hashlib
import json
import random
import shutil
from urllib.parse import quote

from generate_site import (
    ADOPT_PHONE,
    PHONE,
    SITE,
    SITE_ORIGIN,
    contact_section,
    esc,
    footer,
    head,
    nav,
    write,
)
from seo_places import KEYWORDS, PLACES

COPY_PATH = SITE.parent / "data" / "seo_copy.json"
ARTICLES_PATH = SITE.parent / "data" / "seo_articles.json"
ADOPT_P2 = [
    "입양 문의는 {전화}입니다. 함께 살 가족과 사는 환경을 듣고, 찾아보는 {동물}의 나이를 맞춰 만남을 안내합니다. {키워드}는 판매 글이 아니라 상담 뒤 아이를 만나는 절차입니다.",
    "{전화}로 생활 이야기를 먼저 나눕니다. 어떤 {동물}을 찾는지, 돌볼 시간은 어떤지 듣고 만날 수 있는 아이를 고릅니다. {키워드} 비용을 이 페이지에서 정하지는 않습니다.",
    "상담 전화는 {전화}입니다. {동물}의 성격과 건강, 지금 가족을 기다리는 아이를 전화로 설명합니다. {키워드}는 바로 데려가는 신청이 아니라 서로 맞는지 확인하는 과정입니다.",
    "{전화}에서 집의 상황과 찾는 {동물}을 듣습니다. 맞지 않으면 다른 아이를 안내하거나 만남을 미룹니다. {키워드}라고 해서 당일 입양이 되지는 않습니다.",
    "입양을 알아보는 전화는 {전화}입니다. 가족 구성과 사는 곳을 듣고 {동물}을 소개합니다. {키워드}는 보호소 기록을 보고 전화한 뒤 직접 만나는 순서입니다.",
]


def particle_wa(word: str) -> str:
    code = ord(word[-1])
    if 0xAC00 <= code <= 0xD7A3 and (code - 0xAC00) % 28:
        return "과"
    return "와"


def fill(text: str, region: str, phrase: str, animal: str, phone: str) -> str:
    text = text.replace("{동물}과", animal + particle_wa(animal))
    text = (
        text.replace("{지역}", region)
        .replace("{동물}", animal)
        .replace("{전화}", phone)
        .replace("여유 병상", "빈자리")
        .replace("실제 구조와 보호 과정", "실제 보호 과정")
    )
    if "{키워드}" in text:
        text = text.replace("{키워드}", phrase, 1).replace("{키워드}", "상담")
    return text


def image_pool() -> list[str]:
    paths = []
    for folder in (SITE / "photos", SITE / "stories", SITE / "assets" / "rehome"):
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} and path.stat().st_size > 1000:
                paths.append(path.relative_to(SITE).as_posix())
    return sorted(paths)


def page_url(region: str, keyword: str = "") -> str:
    if keyword:
        return f"{SITE_ORIGIN}/k/{quote(region)}/{quote(keyword)}/"
    return f"{SITE_ORIGIN}/k/{quote(region)}/"


def phone_for(intent: str) -> str:
    return ADOPT_PHONE if intent == "adopt" else PHONE


def paragraphs(copy: dict, intent: str, region: str, phrase: str, animal: str, phone: str) -> list[str]:
    bank = copy[intent]
    seed = int(hashlib.sha256(phrase.encode("utf-8")).hexdigest()[:8], 16)
    picker = random.Random(seed)
    chosen = []
    for key in ("p1", "p2", "p3", "p4"):
        row = ADOPT_P2 if intent == "adopt" and key == "p2" else bank[key]
        chosen.append(fill(row[picker.randrange(len(row))], region, phrase, animal, phone))
    hooks = bank.get("region_hooks") or []
    if hooks:
        hook = fill(hooks[picker.randrange(len(hooks))], region, phrase, animal, phone)
        chosen.insert(1, hook)
    return chosen


def guide_steps(copy: dict, intent: str, region: str, phrase: str, animal: str, phone: str) -> list[dict]:
    bank = copy.get(intent) or {}
    steps = bank.get("steps") or []
    if not steps:
        return []
    seed = int(hashlib.sha256(f"steps:{phrase}".encode("utf-8")).hexdigest()[:8], 16)
    picker = random.Random(seed)
    order = list(range(len(steps)))
    picker.shuffle(order)
    picked = []
    for index in order[:6]:
        row = steps[index]
        picked.append(
            {
                "title": fill(row.get("title") or "", region, phrase, animal, phone),
                "lead": fill(row.get("lead") or "", region, phrase, animal, phone),
                "body": fill(row.get("body") or "", region, phrase, animal, phone),
                "checks": [
                    fill(item, region, phrase, animal, phone) for item in (row.get("checks") or [])[:3]
                ],
            }
        )
    return picked


def extended_faqs(copy: dict, intent: str, region: str, phrase: str, animal: str, phone: str) -> list[tuple[str, str]]:
    bank = copy.get(intent) or {}
    rows = bank.get("faq") or []
    seed = int(hashlib.sha256(f"faq:{phrase}".encode("utf-8")).hexdigest()[:8], 16)
    picker = random.Random(seed)
    if len(rows) > 4:
        rows = picker.sample(rows, 4)
    pairs = []
    for row in rows:
        question = fill(row.get("q") or "", region, phrase, animal, phone)
        answer = fill(row.get("a") or "", region, phrase, animal, phone)
        if question and answer:
            pairs.append((question, answer))
    return pairs


def assemble_long_sections(
    articles: dict,
    intent: str,
    region: str,
    phrase: str,
    animal: str,
    phone: str,
) -> list[dict]:
    bank = articles.get(intent) or {}
    variants = bank.get("variants") or []
    if not variants:
        return []
    seed = int(hashlib.sha256(f"art:{phrase}".encode("utf-8")).hexdigest()[:8], 16)
    slot_count = max(len(v.get("sections") or []) for v in variants)
    picked: list[dict] = []
    used: set[tuple[int, int]] = set()
    for slot in range(slot_count):
        vi = (seed + slot * 7 + 1) % len(variants)
        secs = variants[vi].get("sections") or []
        if not secs:
            continue
        si = (seed // (slot + 3) + slot * 2) % len(secs)
        key = (vi, si)
        if key in used:
            si = (si + 1) % len(secs)
            key = (vi, si)
        used.add(key)
        sec = secs[si]
        picked.append(
            {
                "heading": fill(sec.get("heading") or "", region, phrase, animal, phone),
                "subheading": fill(sec.get("subheading") or "", region, phrase, animal, phone),
                "paragraphs": [
                    fill(p, region, phrase, animal, phone) for p in (sec.get("paragraphs") or []) if p
                ],
                "bullets": [
                    fill(b, region, phrase, animal, phone) for b in (sec.get("bullets") or []) if b
                ],
            }
        )
    return picked


def render_long_sections(sections: list[dict]) -> str:
    chunks = []
    for sec in sections:
        if sec.get("heading"):
            chunks.append(f'<h3 class="seo-h3">{esc(sec["heading"])}</h3>')
        if sec.get("subheading"):
            chunks.append(f'<h4 class="seo-h4">{esc(sec["subheading"])}</h4>')
        for paragraph in sec.get("paragraphs") or []:
            chunks.append(f"<p>{esc(paragraph)}</p>")
        bullets = sec.get("bullets") or []
        if bullets:
            items = "".join(f"<li>{esc(item)}</li>" for item in bullets)
            chunks.append(f'<ul class="seo-bullets">{items}</ul>')
    return "".join(chunks)


def watch_lines(copy: dict, intent: str, region: str, phrase: str, animal: str, phone: str) -> list[str]:
    bank = copy.get(intent) or {}
    rows = bank.get("watch") or []
    seed = int(hashlib.sha256(f"watch:{phrase}".encode("utf-8")).hexdigest()[:8], 16)
    picker = random.Random(seed)
    if len(rows) > 3:
        rows = picker.sample(rows, 3)
    return [fill(row, region, phrase, animal, phone) for row in rows if row]


def faqs(region: str, phrase: str, animal: str, phone: str, intent: str) -> list[tuple[str, str]]:
    if intent == "adopt":
        first = (
            f"{phrase}는 어디서 문의하나요?",
            f"입양 상담 전화는 {phone}입니다. {region}에서 {animal} 입양을 알아보면 생활을 듣고 만날 아이를 안내합니다.",
        )
    else:
        first = (
            f"{phrase} 상담 전화는 무엇인가요?",
            f"입소 상담 전화는 {phone}입니다. {region}이라고 해서 바로 맡길 수 있는 것은 아니고, 자리와 아이 상태를 먼저 확인합니다.",
        )
    return [
        first,
        (
            f"{region}에 따로 적힌 보호소 주소가 있나요?",
            f"{phrase} 페이지는 {region} 상담 안내입니다. 이 글에 없는 주소를 그 지역 지점이라고 안내하지 않습니다.",
        ),
        (
            "전화하면 바로 진행되나요?",
            "자리가 없거나 생활이 맞지 않으면 바로 진행되지 않습니다. 전화로 확인한 뒤 만남을 정합니다.",
        ),
    ]


def json_ld(phrase: str, description: str, url: str, pairs: list[tuple[str, str]]) -> str:
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "name": phrase,
                "url": url,
                "description": description,
                "inLanguage": "ko-KR",
                "isPartOf": {"@type": "WebSite", "name": "강아지보호소 품으로", "url": f"{SITE_ORIGIN}/"},
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {"@type": "Answer", "text": answer},
                    }
                    for question, answer in pairs
                ],
            },
        ],
    }
    return json.dumps(graph, ensure_ascii=False).replace("<", "\\u003c")


def blog_section(
    region: str,
    phrase: str,
    parts: list[str],
    photos: list[str],
    depth: str,
    pairs: list[tuple[str, str]],
    steps: list[dict],
    watch: list[str],
    long_html: str,
) -> str:
    intro = "".join(f"<p class=\"seo-intro\">{esc(part)}</p>" for part in parts[1:3])
    step_html = ""
    for row in steps[:3]:
        checks = "".join(f"<li>{esc(item)}</li>" for item in row.get("checks") or [])
        check_block = f"<ul class=\"seo-checks\">{checks}</ul>" if checks else ""
        lead = f"<p class=\"seo-step-lead\">{esc(row.get('lead', ''))}</p>" if row.get("lead") else ""
        step_html += (
            f'<article class="seo-guide-step">'
            f'<h4>{esc(row.get("title", ""))}</h4>'
            f"{lead}"
            f'<p>{esc(row.get("body", ""))}</p>'
            f"{check_block}"
            f"</article>"
        )
    guide = f'<div class="seo-guide">{step_html}</div>' if step_html else ""
    watch_html = ""
    if watch:
        items = "".join(f"<li>{esc(line)}</li>" for line in watch)
        watch_html = f'<div class="seo-watch"><h3>진행 전에 확인할 점</h3><ul>{items}</ul></div>'
    body_core = f'<div class="seo-long-body">{long_html}{guide}{watch_html}</div>'
    images = "".join(
        f'<figure><img src="{depth}{esc(path)}" alt="{esc(phrase)} 안내 사진" loading="lazy"><figcaption>보호 기록 사진</figcaption></figure>'
        for path in photos
    )
    questions = "".join(f"<p><strong>{esc(question)}</strong>{esc(answer)}</p>" for question, answer in pairs)
    others = "".join(
        f'<a href="../{esc(keyword)}/">{esc(region)}{esc(keyword)}</a>'
        for keyword, _animal, _intent in KEYWORDS
        if f"{region}{keyword}" != phrase
    )
    return f"""<section class="section blog" id="guide">
  <div class="wrap">
    <details class="seo-guide-pack">
      <summary class="seo-guide-summary" aria-label="안내 펼치기"><span class="seo-plus" aria-hidden="true"></span></summary>
      <article class="blog-card">
        <p class="eyebrow">안내</p>
        <h2>{esc(phrase)} 상세 안내</h2>
        {intro}
        {body_core}
        <h3 class="seo-faq-title">자주 묻는 질문</h3>
        <div class="faq">{questions}</div>
        <div class="blog-photos">{images}</div>
        <h3>{esc(region)}의 다른 안내</h3>
        <div class="keyword-links">{others}</div>
      </article>
    </details>
  </div>
</section>
"""


def lead_section(phrase: str, answer: str) -> str:
    return f"""<section class="seo-lead">
  <div class="wrap seo-lead-card">
    <p class="eyebrow">LOCAL GUIDE</p>
    <h1>{esc(phrase)}</h1>
    <p class="seo-lead-answer">{esc(answer)}</p>
  </div>
</section>
"""


def build_keyword_pages(pets: list[dict], stories: list[dict], front_body) -> list[str]:
    copy = json.loads(COPY_PATH.read_text(encoding="utf-8"))
    articles = json.loads(ARTICLES_PATH.read_text(encoding="utf-8")) if ARTICLES_PATH.exists() else {}
    pool = image_pool()
    old = SITE / "area"
    if old.exists():
        shutil.rmtree(old)
    urls = [f"{SITE_ORIGIN}/k/"]
    shared = front_body(pets, stories, "../../../", "p")
    shared_region = front_body(pets, stories, "../../", "p")
    index_links = []
    for region in PLACES:
        urls.append(page_url(region))
        keyword_links = []
        for keyword, animal, intent in KEYWORDS:
            phrase = f"{region}{keyword}"
            phone = phone_for(intent)
            parts = paragraphs(copy, intent, region, phrase, animal, phone)
            pairs = faqs(region, phrase, animal, phone, intent)
            pairs = pairs + extended_faqs(copy, intent, region, phrase, animal, phone)
            steps = guide_steps(copy, intent, region, phrase, animal, phone)
            watch = watch_lines(copy, intent, region, phrase, animal, phone)
            long_sections = assemble_long_sections(articles, intent, region, phrase, animal, phone)
            long_html = render_long_sections(long_sections)
            description = parts[0]
            if len(description) > 110:
                description = description[:110].rstrip() + "…"
            url = page_url(region, keyword)
            urls.append(url)
            seed = int(hashlib.sha256(f"img:{phrase}".encode("utf-8")).hexdigest()[:8], 16)
            img_rng = random.Random(seed)
            count = min(6, len(pool))
            photos = img_rng.sample(pool, count)
            image = f"{SITE_ORIGIN}/{photos[0]}"
            depth = "../../../"
            page = head(
                f"{phrase} | 강아지보호소 품으로",
                depth,
                description,
                url,
                image,
                json_ld(phrase, description, url, pairs),
            )
            page += nav(depth, "")
            page += "<main>\n"
            page += lead_section(phrase, parts[0])
            page += shared
            page += blog_section(region, phrase, parts, photos, depth, pairs, steps, watch, long_html)
            page += contact_section()
            page += "\n</main>\n"
            page += footer(depth)
            write(SITE / "k" / region / keyword / "index.html", page)
            keyword_links.append(f'<a href="{esc(keyword)}/">{esc(phrase)}</a>')
        region_page = head(
            f"{region} 강아지파양 · 보호소 · 입양 | 강아지보호소 품으로",
            "../../",
            f"{region} 강아지파양, 고양이파양, 보호소, 입양 상담 안내입니다. 전화는 전국으로 받습니다.",
            page_url(region),
        )
        region_page += nav("../../", "")
        region_page += "<main>\n"
        region_page += shared_region
        region_page += f"""<section class="section" id="region-words">
  <div class="wrap">
    <div class="section-head">
      <div>
        <h1>{esc(region)}</h1>
        <p>{esc(region)}에서 많이 찾는 상담 단어를 모았습니다. 글을 누르면 그 안내로 이동합니다.</p>
      </div>
    </div>
    <div class="keyword-links">{''.join(keyword_links)}</div>
  </div>
</section>
"""
        region_page += contact_section()
        region_page += "\n</main>\n"
        region_page += footer("../../")
        write(SITE / "k" / region / "index.html", region_page)
        index_links.append(f'<a href="{esc(region)}/">{esc(region)}</a>')
    hub = head(
        "지역별 강아지파양 · 보호소 안내 | 강아지보호소 품으로",
        "../",
        "지역과 상담 단어를 고르면 해당 안내 페이지로 이동합니다.",
        f"{SITE_ORIGIN}/k/",
    )
    hub += nav("../", "")
    hub += f"""<main class="wrap board-hero">
  <p class="eyebrow">REGION</p>
  <h1>지역별 안내</h1>
  <p class="lede">지역을 누르면 강아지파양, 보호소, 입양보내기처럼 상담 단어별 글이 있습니다.</p>
  <div class="place-links">{''.join(index_links)}</div>
</main>
"""
    hub += footer("../")
    write(SITE / "k" / "index.html", hub)
    return urls
