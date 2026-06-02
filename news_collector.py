import feedparser
from openai import OpenAI
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from config import OPENAI_API_KEY, NEWS_TOPICS, SEARCH_PERIOD_DAYS, SEMI_NEWS_TOPIC, TECH_TOPIC

_client = None

def get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def fetch_rss_articles(queries: list[str], max_total: int = 10) -> list[dict]:
    """Google News RSS로 최근 7일 기사 수집"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=SEARCH_PERIOD_DAYS)
    seen_urls = set()
    articles = []

    for query in queries:
        # 한국어·일본어 포함 여부로 언어 판단
        has_korean = any('가' <= c <= '힣' for c in query)
        has_japanese = any('぀' <= c <= 'ヿ' or '一' <= c <= '鿿' for c in query)

        if has_korean:
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
        elif has_japanese:
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ja&gl=JP&ceid=JP:ja"
        else:
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en&gl=US&ceid=US:en"

        feed = feedparser.parse(url)

        for entry in feed.entries:
            if not hasattr(entry, "published_parsed") or entry.published_parsed is None:
                continue
            pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if pub_dt < cutoff:
                continue
            link = entry.get("link", "")
            if link in seen_urls:
                continue
            seen_urls.add(link)

            source = ""
            if hasattr(entry, "source"):
                source = entry.source.get("title", "")

            snippet = re.sub(r"<[^>]+>", "", entry.get("summary", ""))[:300]

            articles.append({
                "title": entry.get("title", ""),
                "url": link,
                "source": source,
                "published": pub_dt.strftime("%Y-%m-%d"),
                "snippet": snippet,
            })

        if len(articles) >= max_total:
            break

    return articles[:max_total]


def summarize_with_openai(topic_title: str, articles: list[dict], today: datetime, is_tech: bool = False) -> str:
    """OpenAI GPT-4o-mini로 기사 목록 요약"""
    if not articles:
        return f"이번 주 {topic_title} 관련 기사를 수집하지 못했습니다."

    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"\n[기사 {i}]\n제목: {a['title']}\n출처: {a['source']}\n날짜: {a['published']}\nURL: {a['url']}\n미리보기: {a['snippet']}\n"

    trend_label = "반도체 업계 시사점" if is_tech else "이 주의 트렌드"
    trend_desc = "한국 반도체 기업 관점에서의 시사점 1문장" if is_tech else "이번 주 이 토픽을 관통하는 트렌드 1문장"

    prompt = f"""당신은 HR 전문 뉴스레터 에디터입니다. 오늘은 {today.strftime('%Y년 %m월 %d일')}입니다.

아래는 최근 수집된 '{topic_title}' 관련 실제 뉴스 기사들입니다.
⚠️ 미국·한국 관련 기사만 선별하세요. 그 외 국가 기사는 제외합니다.
중요한 것 3~5개를 아래 형식으로 정리해주세요.

형식:

### [기사 제목을 한국어로 번역 또는 작성 — 영문 제목 사용 금지]
요약: [핵심 내용 3문장. 기업명·수치·날짜 포함. 미국/한국 중 어느 나라 사례인지 명시. 한국어로 작성.]
출처: [제공된 출처 그대로]
URL: [제공된 URL 그대로]

---

마지막에:
**{trend_label}**: [{trend_desc}]

수집된 기사:
{articles_text}

주의: 제공된 URL을 그대로 사용하세요. 임의로 URL을 만들지 마세요."""

    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def collect_news_for_topic(topic: dict) -> dict:
    today = datetime.now()
    print(f"    RSS 수집 중...")
    articles = fetch_rss_articles(topic["queries"])
    print(f"    기사 {len(articles)}개 수집, GPT-4o-mini 요약 중...")
    content = summarize_with_openai(topic["title"], articles, today)
    return {
        "id": topic["id"],
        "title": topic["title"],
        "emoji": topic["emoji"],
        "content": content,
    }


def collect_semi_news() -> dict:
    """반도체 주요 뉴스 Top 5 수집"""
    today = datetime.now()
    week_ago = today - timedelta(days=SEARCH_PERIOD_DAYS)
    date_range = f"{week_ago.strftime('%Y년 %m월 %d일')} ~ {today.strftime('%Y년 %m월 %d일')}"

    print(f"    RSS 수집 중...")
    articles = fetch_rss_articles(SEMI_NEWS_TOPIC["queries"], max_total=15)
    print(f"    기사 {len(articles)}개 수집, Top 5 선정 중...")

    if not articles:
        return {
            "id": SEMI_NEWS_TOPIC["id"],
            "title": SEMI_NEWS_TOPIC["title"],
            "emoji": SEMI_NEWS_TOPIC["emoji"],
            "content": "이번 주 반도체 뉴스를 수집하지 못했습니다.",
        }

    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"\n[기사 {i}]\n제목: {a['title']}\n출처: {a['source']}\n날짜: {a['published']}\nURL: {a['url']}\n미리보기: {a['snippet']}\n"

    prompt = f"""당신은 반도체 전문 뉴스레터 에디터입니다. 오늘은 {today.strftime('%Y년 %m월 %d일')}입니다.

아래 기사 목록에서 {date_range} 기간 내 한국·미국 관련 반도체 뉴스 중 가장 중요한 5개를 선정해 정리해주세요.
중요도 기준: 산업 영향력, 기술 혁신성, 시장 파급력 순.

각 기사마다 아래 형식으로 작성하세요:

### [기사 제목을 한국어로 번역 또는 작성 — 영문 제목 사용 금지]
요약: [핵심 내용 3문장. 무슨 일이 있었는지, 의미가 무엇인지, 업계 영향이 무엇인지. 한국어로 작성.]
출처: [제공된 출처 그대로]
URL: [제공된 URL 그대로]

---

수집된 기사:
{articles_text}

주의: 제공된 URL을 그대로 사용하세요. 임의로 URL을 만들지 마세요."""

    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.3,
    )
    content = response.choices[0].message.content.strip()

    return {
        "id": SEMI_NEWS_TOPIC["id"],
        "title": SEMI_NEWS_TOPIC["title"],
        "emoji": SEMI_NEWS_TOPIC["emoji"],
        "content": content,
    }


def collect_tech_highlight() -> dict:
    today = datetime.now()
    print(f"    RSS 수집 중...")
    articles = fetch_rss_articles(TECH_TOPIC["queries"], max_total=15)
    print(f"    기사 {len(articles)}개 수집, 핵심 기술 선정 및 해설 작성 중...")

    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"\n[기사 {i}] {a['title']} ({a['published']}, {a['source']})\n미리보기: {a['snippet']}\n"

    prompt = f"""당신은 반도체 기술 전문가이자 교육 콘텐츠 작성자입니다. 오늘은 {today.strftime('%Y년 %m월 %d일')}입니다.

아래 뉴스 기사 목록을 분석하여, 이번 주 반도체 업계에서 가장 많이 언급된 기술 키워드 1개를 선정하세요.
특정 기업의 동향이나 실적이 아닌, **기술 그 자체**를 선정하세요.

그 기술이 무엇인지, 반도체를 잘 모르는 사람도 개념을 이해할 수 있도록 명확하게 설명해주세요.
억지스러운 비유는 쓰지 말고, 기술의 개념과 원리를 직접적으로 설명하세요.

반드시 아래 형식으로 작성하세요:

### 🔍 이번 주 주목 기술: [기술명]

**한 줄 정의**
[이 기술이 무엇인지 한 문장으로 정의]

**기술 개요**
[이 기술의 개념과 작동 원리를 3~4문장으로 설명. 핵심 개념어는 괄호 안에 간단히 부연 설명.]

**왜 주목받고 있나**
[이 기술이 현재 반도체 산업에서 중요한 이유를 2~3문장으로 설명. 기업명은 언급하지 말 것.]

**반도체 종사자가 알아야 할 포인트**
[이 기술이 반도체 설계·제조·소재 관점에서 갖는 의미를 2문장으로 설명.]

---

분석할 뉴스 기사:
{articles_text}"""

    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.5,
    )
    content = response.choices[0].message.content.strip()

    return {
        "id": TECH_TOPIC["id"],
        "title": TECH_TOPIC["title"],
        "emoji": TECH_TOPIC["emoji"],
        "content": content,
    }


def collect_all_news() -> tuple[list[dict], dict, dict]:
    results = []
    print(f"뉴스 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"방식: Google News RSS + GPT-4o-mini 요약")

    for i, topic in enumerate(NEWS_TOPICS):
        if i > 0:
            time.sleep(3)
        print(f"  [{topic['title']}] 수집 중...")
        try:
            result = collect_news_for_topic(topic)
            results.append(result)
            print(f"  [{topic['title']}] 완료")
        except Exception as e:
            print(f"  [{topic['title']}] 오류: {e}")
            results.append({
                "id": topic["id"],
                "title": topic["title"],
                "emoji": topic["emoji"],
                "content": f"이번 주 수집 중 오류가 발생했습니다: {str(e)}",
            })

    time.sleep(3)
    print(f"  [{SEMI_NEWS_TOPIC['title']}] 수집 중...")
    try:
        semi_result = collect_semi_news()
        print(f"  [{SEMI_NEWS_TOPIC['title']}] 완료")
    except Exception as e:
        print(f"  [{SEMI_NEWS_TOPIC['title']}] 오류: {e}")
        semi_result = {
            "id": SEMI_NEWS_TOPIC["id"],
            "title": SEMI_NEWS_TOPIC["title"],
            "emoji": SEMI_NEWS_TOPIC["emoji"],
            "content": f"이번 주 수집 중 오류가 발생했습니다: {str(e)}",
        }

    time.sleep(3)
    print(f"  [{TECH_TOPIC['title']}] 수집 중...")
    try:
        tech_result = collect_tech_highlight()
        print(f"  [{TECH_TOPIC['title']}] 완료")
    except Exception as e:
        print(f"  [{TECH_TOPIC['title']}] 오류: {e}")
        tech_result = {
            "id": TECH_TOPIC["id"],
            "title": TECH_TOPIC["title"],
            "emoji": TECH_TOPIC["emoji"],
            "content": f"이번 주 수집 중 오류가 발생했습니다: {str(e)}",
        }

    return results, semi_result, tech_result
