import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_live_market_events():
    """
    네이버 금융의 실적/기업 일정 페이지를 정밀 분석하여
    국내 10대 대기업 실적뿐만 아니라 ADR, 주총, 배당, 증자 등 굵직한 증시 이벤트를 자동 포착합니다.
    """
    print("🌐 네이버 금융에서 기업 주요 이벤트 및 ADR 일정을 탐색 중...")
    now = datetime.now()
    year = now.year
    month = now.month
    
    url = f"https://finance.naver.com/news/e_calendar.naver?year={year}&month={str(month).zfill(2)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    scraped_events = []
    
    # 우리가 집중 모니터링할 핵심 키워드 및 대형주 목록
    heavyweight_keywords = ["ADR", "DR분할", "주주총회", "배당락", "무상증자", "유상증자", "신규상장", "공모청약"]
    core_companies = ["삼성전자", "SK하이닉스", "LG에너지솔루션", "삼성바이오로직스", "현대차", "기아", "셀트리온", "네이버", "NAVER"]

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            calendar_table = soup.find('table', {'class': 'calendar_table'})
            
            if calendar_table:
                td_elements = calendar_table.find_all('td')
                for td in td_elements:
                    date_div = td.find('div', {'class': 'date'})
                    if not date_div or not date_div.text.strip():
                        continue
                    
                    day_text = date_div.text.strip()
                    event_date = f"{year}-{str(month).zfill(2)}-{str(day_text).zfill(2)}"
                    
                    # 해당 날짜의 등록된 링크(텍스트)들 싹 긁기
                    corp_links = td.find_all('a')
                    for link in corp_links:
                        text = link.text.strip()
                        
                        # 1. SK하이닉스 ADR 및 주요 기업 특이 일정 자동 포착
                        is_important = any(kw in text for kw in heavyweight_keywords)
                        is_core_company = any(comp in text for comp in core_companies)
                        
                        if is_important or is_core_company:
                            # 카테고리 및 아이콘 자동 분류
                            category = "MARKET"
                            importance = "MEDIUM"
                            icon = "📊"
                            
                            if "ADR" in text or "DR" in text:
                                icon = "✈️"
                                importance = "HIGH"
                                text = f"[해외증시] {text}"
                            elif any(kw in text for kw in ["증자", "상장", "청약"]):
                                icon = "💰"
                                importance = "HIGH"
                            elif "주주총회" in text or "주총" in text:
                                icon = "🏛️"
                            
                            event_id = f"auto-{event_date}-{hash(text) % 100000}"
                            
                            scraped_events.append({
                                "id": event_id,
                                "title": f"{icon} {text}",
                                "category": category,
                                "importance": importance,
                                "start_date": event_date,
                                "end_date": event_date,
                                "kst_announcement": f"{event_date} 당일 일정",
                                "description": f"네이버 금융 캘린더 자동 수집 시스템: 시장 변동성 및 수급에 영향을 줄 수 있는 굵직한 주요 기업/종목 스케줄입니다."
                            })
    except Exception as e:
        print(f"❌ 기업 일정 크롤링 중 오류 발생: {e}")
        
    return scraped_events

def get_breaking_market_news():
    """
    네이버 금융 주요 뉴스 헤드라인을 실시간으로 긁어, 
    증시를 뒤흔드는 초대형 키워드가 발견되면 오늘 날짜의 '빅뉴스 알림'으로 자동 등록합니다.
    """
    print("📰 실시간 국내외 증시 빅뉴스 스캐닝 중...")
    url = "https://finance.naver.com/news/mainnews.naver"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    news_events = []
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 증시에 강력한 충격을 주는 핵심 키워드들
    shock_keywords = ["어닝쇼크", "어닝서프라이즈", "금리인하", "금리인상", "디폴트", "긴급발표", "구속", "합병", "ADR발행"]
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 주요 뉴스 제목을 품고 있는 클래스 탐색
            subjects = soup.select('.articleSubject a, .blocka, .title')
            
            for sub in subjects:
                title_text = sub.text.strip()
                
                # 뉴스 제목 중 증시 타격이 큰 키워드가 포함되어 있는지 확인
                if any(kw in title_text for kw in shock_keywords):
                    news_events.append({
                        "id": f"news-{today_str}-{hash(title_text) % 1000}",
                        "title": f"🚨 [속보] {title_text[:28]}...",
                        "category": "MARKET",
                        "importance": "HIGH",
                        "start_date": today_str,
                        "end_date": today_str,
                        "kst_announcement": f"{today_str} 장중 속보 포착",
                        "description": f"실시간 금융 뉴스 자동 감지: 시장 심리에 지대한 영향을 미칠 수 있는 헤드라인 뉴스입니다.\n원문 헤드라인: {title_text}"
                    })
                    # 달력이 너무 복잡해지지 않도록 최대 2개까지만 반영
                    if len(news_events) >= 2:
                        break
    except Exception as e:
        print(f"❌ 실시간 뉴스 분석 중 오류 발생: {e}")
        
    return news_events

def fetch_macro_data():
    """
    글로벌 거시경제(FOMC 회의록, CPI, PCE 등) 핵심 마스터 데이터
    """
    return [
        { "id": "macro-2026-07-02-fomc-minutes", "title": "[03:00] 🏛️ 6월 FOMC 회의록 공개", "category": "FED", "importance": "MEDIUM", "start_date": "2026-07-02", "end_date": "2026-07-02", "kst_announcement": "2026-07-02 (목) 새벽 03:00", "description": "연준 위원들의 세부 발언록이 공개되어 향후 금리 기조의 결정적 힌트를 제공합니다." },
        { "id": "macro-2026-07-03-emp", "title": "[21:30] 미 고용동향보고서", "category": "INDEX", "importance": "HIGH", "start_date": "2026-07-03", "end_date": "2026-07-03", "kst_announcement": "2026-07-03 (금) 저녁 21:30", "description": "비농업 고용 지표 및 실업률 발표" },
        { "id": "macro-2026-07-14-cpi", "title": "[21:30] 미 소비자물가지수(CPI)", "category": "INDEX", "importance": "HIGH", "start_date": "2026-07-14", "end_date": "2026-07-14", "kst_announcement": "2026-07-14 (화) 저녁 21:30", "description": "미국 인플레이션의 방향타 역할을 하는 핵심 지표" },
        { "id": "macro-2026-07-30-fomc", "title": "[03:00] 🏛️ 7월 FOMC 금리결정", "category": "FED", "importance": "HIGH", "start_date": "2026-07-28", "end_date": "2026-07-29", "kst_announcement": "2026-07-30 (목) 새벽 03:00", "description": "미 연준 기준금리 결정 성명서 및 파월 의장 기자회견" },
        { "id": "macro-2026-07-30-pce", "title": "[21:30] 미 개인소비지출(PCE)", "category": "INDEX", "importance": "HIGH", "start_date": "2026-07-30", "end_date": "2026-07-30", "kst_announcement": "2026-07-30 (목) 저녁 21:30", "description": "연준이 인플레이션 판단 시 가장 신뢰하는 근원 물가 지표" },
        { "id": "macro-2026-08-20-fomc-minutes", "title": "[03:00] 🏛️ 7월 FOMC 회의록 공개", "category": "FED", "importance": "MEDIUM", "start_date": "2026-08-20", "end_date": "2026-08-20", "kst_announcement": "2026-08-20 (목) 새벽 03:00", "description": "7월 진행된 금리 결정 회의의 상세 의사록 의무 공개일입니다." },
        { "id": "macro-2026-09-17-fomc", "title": "[03:00] 🏛️ 9월 FOMC (점도표★)", "category": "FED", "importance": "HIGH", "start_date": "2026-09-15", "end_date": "2026-09-16", "kst_announcement": "2026-09-17 (목) 새벽 03:00", "description": "향후 금리 전망 점도표가 함께 공개되는 슈퍼 위크입니다." },
        { "id": "macro-2026-10-08-fomc-minutes", "title": "[03:00] 🏛️ 9월 FOMC 회의록 공개", "category": "FED", "importance": "MEDIUM", "start_date": "2026-10-08", "end_date": "2026-10-08", "kst_announcement": "2026-10-08 (목) 새벽 03:00", "description": "9월 FOMC 회의의 상세 기록이 베일을 벗는 날입니다." }
    ]

def main():
    # 1. 글로벌 매크로 기본 데이터 로드
    all_events = fetch_macro_data()
    existing_ids = {e['id'] for e in all_events}
    
    # 2. 실시간 대형 기업 이벤트 및 ADR 크롤링 결합
    live_events = get_live_market_events()
    for le in live_events:
        if le['id'] not in existing_ids:
            all_events.append(le)
            existing_ids.add(le['id'])
            
    # 3. 실시간 장중 속보/빅뉴스 필터링 결합
    breaking_news = get_breaking_market_news()
    for news in breaking_news:
        if news['id'] not in existing_ids:
            all_events.append(news)
            existing_ids.add(news['id'])

    # 4. JSON 파일 저장 업데이트
    with open('stock_calendar_2026.json', 'w', encoding='utf-8') as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)
        
    print(f"🚀 [지능형 자동수집 완료] 총 {len(all_events)}개의 고순도 일정이 캘린더에 동적 주입되었습니다.")

if __name__ == "__main__":
    main()
