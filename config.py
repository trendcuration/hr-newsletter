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
            "corporate restructuring layoffs 2025",
            "organizational transformation company culture",
            "기업 구조조정 조직개편 2025",
        ],
    },
    {
        "id": "compensation",
        "title": "평가/보상",
        "emoji": "💰",
        "queries": [
            "executive compensation salary trends 2025",
            "performance management review system",
            "성과평가 보상체계 임금 2025",
        ],
    },
    {
        "id": "workforce",
        "title": "인력운영",
        "emoji": "👥",
        "queries": [
            "talent management hiring workforce 2025",
            "remote work hybrid policy",
            "채용 인력운영 리텐션 2025",
        ],
    },
    {
        "id": "labor",
        "title": "노사",
        "emoji": "⚖️",
        "queries": [
            "labor union strike workers rights 2025",
            "collective bargaining employment law",
            "노사관계 파업 단체교섭 2025",
        ],
    },
    {
        "id": "ai_hr",
        "title": "AI in HR",
        "emoji": "🤖",
        "queries": [
            "AI human resources recruiting automation 2025",
            "generative AI HR tools workforce planning",
            "HR AI 인사관리 자동화 2025",
        ],
    },
]

# 반도체 기술 하이라이트 섹션
TECH_TOPIC = {
    "id": "tech_highlight",
    "title": "이 주의 핫 기술",
    "emoji": "💡",
    "queries": [
        "semiconductor chip technology breakthrough 2025",
        "TSMC Samsung Intel HBM advanced packaging 2025",
        "삼성전자 SK하이닉스 반도체 기술 2025",
    ],
}
