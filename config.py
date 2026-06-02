import os

# 뉴스레터 제목
NEWSLETTER_TITLE = "주간 HR 뉴스레터"

# OpenAI API
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Gmail SMTP 설정
GMAIL_USER = os.environ.get("GMAIL_USER", "i.garam.lee@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")  # Google 앱 비밀번호

# 수신자 목록
RECIPIENTS = [
    "i.garam.lee@gmail.com",
    "ga-ram.lee@samsung.com",
]

# 뉴스 수집 설정
SEARCH_PERIOD_DAYS = 7  # 최근 7일치 뉴스
NEWS_TOPICS = [
    {
        "id": "organization",
        "title": "조직",
        "emoji": "🏢",
        "queries": [
            "US corporate restructuring layoffs 2025",
            "기업 구조조정 조직개편 한국 2025",
        ],
    },
    {
        "id": "compensation",
        "title": "평가/보상",
        "emoji": "💰",
        "queries": [
            "US executive compensation salary trends 2025",
            "성과평가 보상체계 임금 한국 2025",
        ],
    },
    {
        "id": "workforce",
        "title": "인력운영",
        "emoji": "👥",
        "queries": [
            "US talent management hiring workforce 2025",
            "채용 인력운영 리텐션 한국 2025",
        ],
    },
    {
        "id": "labor",
        "title": "노사",
        "emoji": "⚖️",
        "queries": [
            "US labor union strike employment law 2025",
            "노사관계 파업 단체교섭 한국 2025",
        ],
    },
    {
        "id": "ai_hr",
        "title": "AI in HR",
        "emoji": "🤖",
        "queries": [
            "US AI human resources recruiting automation 2025",
            "HR AI 인사관리 자동화 한국 2025",
        ],
    },
]

# 반도체 기술 하이라이트 섹션 (이번 주 가장 주목받은 기술을 쉽게 설명)
TECH_TOPIC = {
    "id": "tech_highlight",
    "title": "이 주의 반도체 기술 해설",
    "emoji": "💡",
    "queries": [
        "semiconductor technology trending news 2025",
        "반도체 기술 이슈 동향 2025",
        "Samsung SK hynix TSMC chip technology 2025",
    ],
}
