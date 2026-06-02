import feedparser
from openai import OpenAI
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from config import OPENAI_API_KEY, NEWS_TOPICS, SEARCH_PERIOD_DAYS, TECH_TOPIC

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
        is_korean = any(ord(c) > 127 for c in query)
        if is_korean:
            url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
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
중요한 것 3~5개를 아래 형식으로 정리해주세요.

형식:

### [기사 제목을 한국어로 번역 또는 작성 — 영문 제목 사용 금지]
요약: [핵심 내용 3문장. 기업명·수치·날짜 포함. 한국어로 작성.]
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


def collect_tech_highlight() -> dict:
    today = datetime.now()
    print(f"    RSS 수집 중...")
    articles = fetch_rss_articles(TECH_TOPIC["queries"])
    print(f"    기사 {len(articles)}개 수집, GPT-4o-mini 요약 중...")
    content = summarize_with_openai(TECH_TOPIC["title"], articles, today, is_tech=True)
    return {
        "id": TECH_TOPIC["id"],
        "title": TECH_TOPIC["title"],
        "emoji": TECH_TOPIC["emoji"],
        "content": content,
    }


def collect_all_news() -> tuple[list[dict], dict]:
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

    return results, tech_result
