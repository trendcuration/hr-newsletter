import re
from datetime import datetime
from config import NEWSLETTER_TITLE, NEWS_TOPICS


def parse_articles(content: str) -> list[dict]:
    """### 제목 / 요약 / 출처 / URL 구조를 파싱하여 기사 목록 반환"""
    articles = []
    trend_line = ""

    # 이 주의 트렌드 / 반도체 업계 시사점 추출
    trend_match = re.search(r"\*\*(이 주의 트렌드|반도체 업계 시사점)\*\*[:\s]*(.+)", content)
    if trend_match:
        trend_line = trend_match.group(2).strip()

    # ### 로 시작하는 기사 블록 분할
    blocks = re.split(r"\n(?=###\s)", content)
    for block in blocks:
        block = block.strip()
        if not block.startswith("###"):
            continue

        title_match = re.match(r"###\s+(.+)", block)
        if not title_match:
            continue
        title = title_match.group(1).strip()

        summary_match = re.search(r"요약[:\s]+(.+?)(?=\n출처|\n URL|\nURL|$)", block, re.DOTALL)
        source_match = re.search(r"출처[:\s]+(.+)", block)
        url_match = re.search(r"URL[:\s]+(https?://\S+)", block)

        articles.append({
            "title": title,
            "summary": summary_match.group(1).strip() if summary_match else "",
            "source": source_match.group(1).strip() if source_match else "",
            "url": url_match.group(1).strip() if url_match else "",
        })

    return articles, trend_line


def build_article_card(article: dict, index: int) -> str:
    number_badges = ["①", "②", "③", "④", "⑤"]
    badge = number_badges[index] if index < len(number_badges) else f"{index+1}."

    link_html = ""
    if article["url"]:
        link_html = f'<a class="read-more" href="{article["url"]}" target="_blank">원문 읽기 →</a>'

    source_html = f'<span class="article-source">{article["source"]}</span>' if article["source"] else ""

    return f"""
    <div class="article-card">
      <div class="article-title-row">
        <span class="article-badge">{badge}</span>
        <h3 class="article-title">{article["title"]}</h3>
      </div>
      <p class="article-summary">{article["summary"]}</p>
      <div class="article-footer">
        {source_html}
        {link_html}
      </div>
    </div>"""


def build_topic_section(topic: dict, anchor_id: str) -> str:
    articles, trend_line = parse_articles(topic["content"])

    if articles:
        cards_html = "\n".join(build_article_card(a, i) for i, a in enumerate(articles))
    else:
        # 파싱 실패 시 원문 텍스트 그대로 표시
        cards_html = f'<div class="fallback-content">{topic["content"]}</div>'

    trend_html = ""
    if trend_line:
        trend_html = f'<div class="trend-bar">📌 {trend_line}</div>'

    return f"""
  <div class="topic-section" id="{anchor_id}">
    <div class="topic-header">
      <span class="topic-emoji">{topic["emoji"]}</span>
      <span class="topic-title">{topic["title"]}</span>
    </div>
    <div class="topic-content">
      {cards_html}
      {trend_html}
    </div>
  </div>"""


def build_tech_section(tech_result: dict) -> str:
    articles, trend_line = parse_articles(tech_result["content"])

    if articles:
        cards_html = "\n".join(build_article_card(a, i) for i, a in enumerate(articles))
    else:
        cards_html = f'<div class="fallback-content">{tech_result["content"]}</div>'

    trend_html = ""
    if trend_line:
        trend_html = f'<div class="trend-bar tech-trend-bar">💬 {trend_line}</div>'

    return f"""
  <div class="tech-section" id="tech">
    <div class="tech-badge">🔬 반도체 기술 동향</div>
    <div class="tech-header">
      <span class="topic-emoji">{tech_result["emoji"]}</span>
      <span class="topic-title">{tech_result["title"]}</span>
    </div>
    <div class="topic-content">
      {cards_html}
      {trend_html}
    </div>
  </div>"""


def build_toc(topics: list[dict], has_tech: bool) -> str:
    items = []
    for t in topics:
        items.append(
            f'<a href="#{t["id"]}" class="toc-item"><span class="toc-emoji">{t["emoji"]}</span>{t["title"]}</a>'
        )
    if has_tech:
        items.append('<a href="#tech" class="toc-item toc-tech"><span class="toc-emoji">💡</span>이 주의 핫 기술</a>')
    return f'<div class="toc">{"".join(items)}</div>'


def build_email_html(news_results: list[dict], tech_result: dict | None = None) -> str:
    today = datetime.now()
    week_num = today.isocalendar()[1]
    date_str = today.strftime("%Y년 %m월 %d일")

    topics_html = "\n".join(
        build_topic_section(t, t["id"]) for t in news_results
    )
    tech_html = build_tech_section(tech_result) if tech_result else ""
    toc_html = build_toc(news_results, tech_result is not None)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{NEWSLETTER_TITLE}</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', '맑은 고딕', sans-serif;
    background: #f0f2f5;
    margin: 0;
    padding: 20px 0;
    color: #333;
  }}
  .container {{
    max-width: 700px;
    margin: 0 auto;
    background: #ffffff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  }}

  /* ── 헤더 ── */
  .header {{
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2d45 50%, #1a3a5c 100%);
    color: white;
    padding: 40px 44px 32px;
    text-align: center;
  }}
  .header-label {{
    font-size: 11px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #7eb8e8;
    margin-bottom: 10px;
  }}
  .header-title {{
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0 0 6px;
  }}
  .header-sub {{
    font-size: 13px;
    color: #90cdf4;
    margin: 0;
  }}
  .week-badge {{
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 5px 18px;
    font-size: 12px;
    margin-top: 18px;
    letter-spacing: 0.5px;
  }}

  /* ── 본문 래퍼 ── */
  .body {{
    padding: 32px 40px 40px;
  }}
  .intro {{
    background: #eef5ff;
    border-left: 4px solid #3182ce;
    padding: 14px 18px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 20px;
    font-size: 14px;
    color: #2c5282;
    line-height: 1.6;
  }}

  /* ── 목차 ── */
  .toc {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 32px;
    padding: 16px 18px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
  }}
  .toc-item {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    color: #4a5568;
    text-decoration: none;
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 4px 12px;
    transition: background 0.15s;
  }}
  .toc-item:hover {{ background: #ebf4ff; color: #2b6cb0; }}
  .toc-tech {{ border-color: #7b68ee; color: #5a4fcf; }}
  .toc-emoji {{ font-size: 13px; }}

  /* ── 토픽 섹션 ── */
  .topic-section {{
    margin-bottom: 28px;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
  }}
  .topic-header {{
    background: #f8fafc;
    padding: 14px 22px;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .topic-emoji {{ font-size: 20px; }}
  .topic-title {{
    font-size: 16px;
    font-weight: 700;
    color: #1a202c;
    letter-spacing: -0.3px;
  }}
  .topic-content {{ padding: 16px 20px 20px; }}

  /* ── 기사 카드 ── */
  .article-card {{
    background: #fafbfc;
    border: 1px solid #e8edf2;
    border-left: 4px solid #3182ce;
    border-radius: 0 8px 8px 0;
    padding: 14px 16px;
    margin-bottom: 14px;
  }}
  .article-card:last-of-type {{ margin-bottom: 0; }}
  .article-title-row {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 8px;
  }}
  .article-badge {{
    font-size: 15px;
    flex-shrink: 0;
    margin-top: 1px;
  }}
  .article-title {{
    font-size: 14px;
    font-weight: 700;
    color: #1a202c;
    margin: 0;
    line-height: 1.5;
    letter-spacing: -0.2px;
  }}
  .article-summary {{
    font-size: 13px;
    color: #4a5568;
    line-height: 1.75;
    margin: 0 0 10px;
  }}
  .article-footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }}
  .article-source {{
    font-size: 11px;
    color: #a0aec0;
    font-weight: 500;
    letter-spacing: 0.3px;
  }}
  .read-more {{
    font-size: 12px;
    color: #3182ce;
    text-decoration: none;
    font-weight: 600;
    white-space: nowrap;
  }}
  .read-more:hover {{ text-decoration: underline; }}

  /* ── 트렌드 바 ── */
  .trend-bar {{
    margin-top: 16px;
    background: #fffbeb;
    border: 1px solid #f6e05e;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #744210;
    line-height: 1.6;
  }}
  .tech-trend-bar {{
    background: #f0edff;
    border-color: #b794f4;
    color: #44337a;
  }}

  /* ── 반도체 기술 섹션 ── */
  .tech-section {{
    margin-bottom: 28px;
    border: 2px solid #7b68ee;
    border-radius: 12px;
    overflow: hidden;
    background: linear-gradient(180deg, #f8f6ff 0%, #fff 60%);
  }}
  .tech-badge {{
    background: linear-gradient(90deg, #7b68ee, #5a4fcf);
    color: white;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 6px 22px;
  }}
  .tech-header {{
    background: #f3f0ff;
    padding: 14px 22px;
    border-bottom: 1px solid #d6d0f7;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .tech-section .article-card {{
    border-left-color: #7b68ee;
  }}
  .tech-section .article-title {{ color: #2d3748; }}
  .tech-section .read-more {{ color: #5a4fcf; }}

  /* ── fallback ── */
  .fallback-content {{
    font-size: 13px;
    color: #4a5568;
    line-height: 1.8;
    white-space: pre-wrap;
  }}

  /* ── 푸터 ── */
  .footer {{
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
    padding: 24px 40px;
    text-align: center;
    font-size: 12px;
    color: #a0aec0;
    line-height: 1.8;
  }}
  .footer a {{ color: #718096; text-decoration: none; }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <div class="header-label">HR Intelligence</div>
    <h1 class="header-title">{NEWSLETTER_TITLE}</h1>
    <p class="header-sub">글로벌 HR 트렌드 주간 요약 + 반도체 기술 동향</p>
    <div class="week-badge">{week_num}주차 &middot; {date_str}</div>
  </div>

  <div class="body">
    <div class="intro">
      이번 주 글로벌 HR 주요 기사와 반도체 기술 동향을 정리했습니다.
      미국·유럽 기업 중심으로 조직, 보상, 인력운영, 노사, AI/HR 5개 영역을 커버하며,
      마지막 섹션에서 이 주의 핫 반도체 기술을 소개합니다.
    </div>

    {toc_html}

    {topics_html}

    {tech_html}
  </div>

  <div class="footer">
    <p>{NEWSLETTER_TITLE} &middot; 매주 월요일 발송</p>
    <p>본 뉴스레터는 Claude AI가 글로벌 뉴스를 자동 수집·요약하여 제공합니다.</p>
  </div>

</div>
</body>
</html>"""


def build_email_subject() -> str:
    today = datetime.now()
    week_num = today.isocalendar()[1]
    return f"[{NEWSLETTER_TITLE}] {today.strftime('%Y년 %m월 %d일')} · {week_num}주차"
