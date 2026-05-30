#!/usr/bin/env python3
"""주간 HR 뉴스레터 - 자동 수집 및 발송"""

import sys
from datetime import datetime
from news_collector import collect_all_news
from email_template import build_email_html, build_email_subject
from email_sender import send_newsletter


def save_html_preview(html: str):
    filename = f"preview_{datetime.now().strftime('%Y%m%d')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"미리보기 저장: {filename}")


def run(preview_only: bool = False):
    print("=" * 50)
    print("주간 HR 뉴스레터 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. 뉴스 수집 (HR 토픽 + 반도체 기술)
    news_results, tech_result = collect_all_news()

    # 2. 이메일 빌드
    html = build_email_html(news_results, tech_result)
    subject = build_email_subject()

    print(f"\n제목: {subject}")

    # 3. 미리보기 저장 (항상)
    save_html_preview(html)

    # 4. 발송 (preview_only 아닐 때)
    if preview_only:
        print("\n[미리보기 모드] 메일 발송 생략. preview_YYYYMMDD.html 파일을 브라우저로 확인하세요.")
    else:
        send_newsletter(subject, html)

    print("\n완료!")


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    run(preview_only=preview)
