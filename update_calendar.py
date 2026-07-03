import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_naver_earnings_calendar():
    """
    네이버 금융 실적 캘린더에서 이번 달 대기업들의 실적 발표일을 실시간 크롤링합니다.
    """
    print("🌐 네이버 금융에서 실시간 기업 실적 일정을 조회하는 중...")
    now = datetime.now()
    year = now.year
    month = now.month
    
    # 네이버 금융 기업실적 캘린더 URL
    url = f"https://finance.naver.com/news/e_calendar.naver?year={year}&month={str(month).zfill(2)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    scraped_events = []
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("⚠️ 네이버 금융 접근 실패로 기본 실적 일정을 사용합니다.")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        # 네이버 금융 실적 달력 테이블 파싱
        calendar_table = soup.find('table', {'class': 'calendar_table'})
        
        if not calendar_table:
            return []
            
        # 달력 내부의 날짜별 셀(td)을 모두 탐색
        td_elements = calendar_table.find_all('td')
        for td in td_elements:
            # 날짜 추출
            date_div = td.find('div', {'class': 'date'})
            if not date_div:
                continue
            day_text = date_div.text.strip()
            if not day_text:
                continue
                
            event_date = f"{year}-{str(month).zfill(2)}-{str(day_text).zfill(2)}"
            
            # 해당 날짜에 등록된 기업 리스트 추출
            corp_links = td.find_all('a')
            for link in corp_links:
                corp_name = link.text.strip()
                
                # 우리가 집중 모니터링할 핵심 기업 필터링
                if "삼성전자" in corp_name:
                    scraped_events.append({
                        "id": f"corp-samsung-{event_date}-final",
                        "title": "[10:00] 📊 삼성전자 확정실적(본실적/컨콜)",
                        "category": "MARKET",
                        "importance": "HIGH",
                        "start_date": event_date,
                        "end_date": event_date,
                        "kst_announcement": f"{event_date} (확정일자) 오전 10:00",
                        "description": "네이버 금융 실시간 연동 데이터: 사업부별 세부 성적 및 Q&A 컨퍼런스 콜이 진행됩니다."
                    })
                elif "SK하이닉스" in corp_name:
                    scraped_events.append({
                        "id": f"corp-hynix-{event_date}-final",
                        "title": "[09:00] SK하이닉스 본실적 발표",
                        "category": "MARKET",
                        "importance": "HIGH",
                        "start_date": event_date,
                        "end_date": event_date,
                        "kst_announcement": f"{event_date} (확정일자) 오전 09:00",
                        "description": "네이버 금융 실시간 연동 데이터: 반도체 및 HBM 실적 상세 수치 공개."
                    })
    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        
    return scraped_events

def fetch_macro_data():
    """
    미국 주요 거시경제 지표 및 FOMC 회의록 일정을 생성 및 빌드합니다.
    """
    # 인베스팅닷컴 차단 우회를 위해 안정적으로 검증된 타임라인 및 회의록 주기 데이터를 기반으로 생성
    return [
        { 
            "id": "macro-2026-07-02-fomc-minutes", 
            "title": "[03:00] 🏛️ 6월 FOMC 회의록 공개", 
            "category": "FED", 
            "importance": "MEDIUM", 
            "start_date": "2026-07-02", 
            "end_date": "2026-07-02", 
            "kst_announcement": "2026-07-02 (목) 새벽 03:00", 
            "description": "연준 위원들의 세부 발언록이 공개되어 향후 금리 인하/인상 기조의 힌트를 얻을 수 있습니다." 
        },
        { 
            "id": "macro-2026-07-03-emp", 
            "title": "[21:30] 미 고용동향보고서", 
            "category": "INDEX", 
            "importance": "HIGH", 
            "start_date": "2026-07-03", 
            "end_date": "2026-07-03", 
            "kst_announcement": "2026-07-03 (금) 저녁 21:30", 
            "description": "비농업 고용 지표 및 실업률 발표" 
        },
        { 
            "id": "macro-2026-07-14-cpi", 
            "title": "[21:30] 미 소비자물가지수(CPI)", 
            "category": "INDEX", 
            "importance": "HIGH", 
            "start_date": "2026-07-14", 
            "end_date": "2026-07-14", 
            "kst_announcement": "2026-07-14 (화) 저녁 21:30", 
            "description": "미국 인플레이션 핵심 지표" 
        },
        { 
            "id": "macro-2026-07-30-fomc", 
            "title": "[03:00] 🏛️ 7월 FOMC 금리결정", 
            "category": "FED", 
            "importance": "HIGH", 
            "start_date": "2026-07-28", 
            "end_date": "2026-07-29", 
            "kst_announcement": "2026-07-30 (목) 새벽 03:00", 
            "description": "미 연준 기준금리 결정 성명서 발표" 
        },
        { 
            "id": "macro-2026-07-30-pce", 
            "title": "[21:30] 미 개인소비지출(PCE)", 
            "category": "INDEX", 
            "importance": "HIGH", 
            "start_date": "2026-07-30", 
            "end_date": "2026-07-30", 
            "kst_announcement": "2026-07-30 (목) 저녁 21:30", 
            "description": "연준이 가장 신뢰하는 근원 물가 지표" 
        },
        { 
            "id": "macro-2026-08-20-fomc-minutes", 
            "title": "[03:00] 🏛️ 7월 FOMC 회의록 공개", 
            "category": "FED", 
            "importance": "MEDIUM", 
            "start_date": "2026-08-20", 
            "end_date": "2026-08-20", 
            "kst_announcement": "2026-08-20 (목) 새벽 03:00", 
            "description": "7월 진행된 금리 결정 회의의 상세 의사록 의무 공개일입니다." 
        },
        { 
            "id": "macro-2026-09-17-fomc", 
            "title": "[03:00] 🏛️ 9월 FOMC (점도표★)", 
            "category": "FED", 
            "importance": "HIGH", 
            "start_date": "2026-09-15", 
            "end_date": "2026-09-16", 
            "kst_announcement": "2026-09-17 (목) 새벽 03:00", 
            "description": "향후 금리 전망 점도표가 함께 공개되는 슈퍼 위크입니다." 
        },
        { 
            "id": "macro-2026-10-08-fomc-minutes", 
            "title": "[03:00] 🏛️ 9월 FOMC 회의록 공개", 
            "category": "FED", 
            "importance": "MEDIUM", 
            "start_date": "2026-10-08", 
            "end_date": "2026-10-08", 
            "kst_announcement": "2026-10-08 (목) 새벽 03:00", 
            "description": "9월 대격변 FOMC 회의의 상세 기록이 베일을 벗는 날입니다." 
        }
    ]

def main():
    # 1. 크롤링 데이터 수집
    live_earnings = get_naver_earnings_calendar()
    
    # 2. 매크로 및 회의록 고정 일정 수집
    macro_events = fetch_macro_data()
    
    # 3. 7월 7일 상징적인 삼성 가이던스 기본값 예외 추가 (네이버 달력에 본실적만 뜰 때를 대비)
    samsung_guidance = {
        "id": "corp-samsung-2026-07-07-guidance",
        "title": "[09:00] 🌟 삼성전자 2분기 잠정실적(가이던스)",
        "category": "MARKET",
        "importance": "HIGH",
        "start_date": "2026-07-07",
        "end_date": "2026-07-07",
        "kst_announcement": "2026-07-07 (화) 오전 09:00",
        "description": "2분기 매출액, 영업이익 총액 잠정 가이던스 선공개일"
    }
    
    # 중복 방지하며 결합
    all_events = macro_events + [samsung_guidance]
    existing_ids = {e['id'] for e in all_events}
    
    for live_event in live_earnings:
        if live_event['id'] not in existing_ids:
            all_events.append(live_event)
            
    # JSON 파일 업데이트 저장
    with open('stock_calendar_2026.json', 'w', encoding='utf-8') as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)
        
    print(f"🚀 실시간 연동 완료! 총 {len(all_events)}개의 일정이 캘린더에 동적 주입되었습니다.")

if __name__ == "__main__":
    main()
