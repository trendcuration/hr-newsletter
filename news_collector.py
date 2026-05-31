import anthropic
import time
from datetime import datetime, timedelta
from config import ANTHROPIC_API_KEY, NEWS_TOPICS, SEARCH_PERIOD_DAYS, TECH_TOPIC


def collect_news_for_topic(client: anthropic.Anthropic, topic: dict) -> dict:
    today = datetime.now()
    week_ago = today - timedelta(days=SEARCH_PERIOD_DAYS)
    date_range = f"{week_ago.strftime('%Y년 %m월 %d일')} ~ {today.strftime('%Y년 %m월 %d일')}"
    queries_text = "\n".join(f"- {q}" for q in topic["queries"])

    prompt = f"""당신은 HR 전문 뉴스레터 에디터입니다.

아래 검색어들을 사용해 최근 1주일({date_range}) 동안의 국내외 HR 뉴스를 검색해주세요.
한국(국내 기업·정부·노동부 동향 포함)과 미국·유럽(글로벌 기업 사례) 기사를 균형 있게 수집해주세요.

검색어:
{queries_text}

실제 검색한 기사 중 중요한 것 3~5개를 아래 형식으로 정리해주세요.
반드시 실제 기사의 제목과 URL을 포함해야 합니다.

각 기사마다:

### [기사 제목을 한국어로 번역 또는 작성 — 영문 제목은 사용하지 말 것]
요약: [핵심 내용을 3문장으로 요약. 구체적 기업명, 수치, 날짜 포함. 한국어로 작성.]
출처: [미디어명 또는 기관명]
URL: [실제 기사 URL]

---

마지막에 한 줄:
**이 주의 트렌드**: [이번 주 이 토픽을 관통하는 트렌드 1문장]

확인되지 않은 내용이나 가상의 URL은 절대 포함하지 마세요."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": prompt}],
    )

    content_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            content_text += block.text

    return {
        "id": topic["id"],
        "title": topic["title"],
        "emoji": topic["emoji"],
        "content": content_text.strip(),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


def collect_tech_highlight(client: anthropic.Anthropic) -> dict:
    today = datetime.now()
    week_ago = today - timedelta(days=SEARCH_PERIOD_DAYS)
    date_range = f"{week_ago.strftime('%Y년 %m월 %d일')} ~ {today.strftime('%Y년 %m월 %d일')}"
    queries_text = "\n".join(f"- {q}" for q in TECH_TOPIC["queries"])

    prompt = f"""당신은 반도체/기술 전문 뉴스레터 에디터입니다.

아래 검색어들을 사용해 최근 1주일({date_range}) 동안 반도체 업계에서 가장 주목받은 기술 뉴스를 검색해주세요.
삼성전자·SK하이닉스 등 한국 기업 관련 국내 기사와 TSMC·Intel·NVIDIA 등 해외 기사를 균형 있게 수집해주세요.

검색어:
{queries_text}

이번 주 가장 핫했던 기술 뉴스 2~3개를 아래 형식으로 정리해주세요.
반드시 실제 기사 제목과 URL을 포함해야 합니다.

각 기사마다:

### [기사 제목을 한국어로 번역 또는 작성 — 영문 제목은 사용하지 말 것]
요약: [핵심 내용을 3문장으로 요약. 기술적 의미, 주요 기업/기관, 업계 영향 포함. 한국어로 작성.]
출처: [미디어명 또는 기관명]
URL: [실제 기사 URL]

---

마지막에 한 줄:
**반도체 업계 시사점**: [한국 반도체 기업 관점에서의 시사점 1문장]

확인되지 않은 내용이나 가상의 URL은 절대 포함하지 마세요."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": prompt}],
    )

    content_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            content_text += block.text

    return {
        "id": TECH_TOPIC["id"],
        "title": TECH_TOPIC["title"],
        "emoji": TECH_TOPIC["emoji"],
        "content": content_text.strip(),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }


def collect_all_news() -> tuple[list[dict], dict]:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    results = []

    print(f"뉴스 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    for i, topic in enumerate(NEWS_TOPICS):
        if i > 0:
            print(f"  (rate limit 방지 대기 75초...)")
            time.sleep(75)
        print(f"  [{topic['title']}] 수집 중...")
        try:
            result = collect_news_for_topic(client, topic)
            results.append(result)
            print(f"  [{topic['title']}] 완료")
        except Exception as e:
            print(f"  [{topic['title']}] 오류: {e}")
            results.append({
                "id": topic["id"],
                "title": topic["title"],
                "emoji": topic["emoji"],
                "content": f"이번 주 수집 중 오류가 발생했습니다: {str(e)}",
                "usage": {"input_tokens": 0, "output_tokens": 0},
            })

    print(f"  (rate limit 방지 대기 75초...)")
    time.sleep(75)
    print(f"  [{TECH_TOPIC['title']}] 수집 중...")
    try:
        tech_result = collect_tech_highlight(client)
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
