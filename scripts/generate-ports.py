#!/usr/bin/env python3
"""
CruiseLink 기항지(Ports) 가이드 페이지 생성기
"""
import json, html, re, sys
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
DATA = BASE / "assets/data"
OUT = BASE / "guide"
(OUT / "ports").mkdir(parents=True, exist_ok=True)
(OUT / "tours").mkdir(parents=True, exist_ok=True)

with open(DATA / "cruises.json", encoding="utf-8") as f:
    all_cruises = json.load(f)

# ──────────────────────────────────────────
# 기항지 정보 (한국어 콘텐츠)
# ──────────────────────────────────────────
PORTS = {
    "barcelona": {
        "nameKo": "바르셀로나",
        "nameEn": "Barcelona",
        "country": "스페인",
        "emoji": "🇪🇸",
        "region": "지중해",
        "cover": "https://images.unsplash.com/photo-1523531294919-4bcd7c65e216?w=1200&q=80",
        "intro": """바르셀로나(Barcelona)는 스페인 카탈루냐 주의 수도이자 지중해 크루즈의 최대 허브 항구입니다. MSC, NCL, 로열 캐리비안 등 주요 크루즈 선사의 지중해 노선 대부분이 바르셀로나를 출발·도착 항으로 사용합니다.

바르셀로나는 천재 건축가 안토니오 가우디(Antoni Gaudí)의 도시로, 사그라다 파밀리아(Sagrada Família), 구엘 공원(Park Güell), 카사 바트요(Casa Batlló) 등 유네스코 세계문화유산이 도시 곳곳에 있습니다. 크루즈 기항 하루만으로는 전부 돌기 어렵지만, 우선순위를 정해 효율적으로 관광할 수 있습니다.

크루즈 항구(Port de Barcelona)에서 시내까지는 택시·버스로 약 15~20분입니다. 바르셀로나는 세계에서 가장 크루즈 이용객이 많은 상위 5개 항구 중 하나입니다.""",
        "highlights": [
            ("🏛️", "사그라다 파밀리아", "가우디의 미완성 성당, 1882년 착공. 입장권 사전 예매 필수"),
            ("🌿", "구엘 공원", "도심 전망대, 모자이크 광장. 오전 일찍 방문 권장"),
            ("🏖️", "바르셀로네타 해변", "항구 옆 도심 해변. 크루즈 터미널에서 도보 가능"),
            ("🛍️", "람블라스 거리", "시내 중심 보행자 거리. 쇼핑·카페·버스킹"),
            ("🎨", "카사 바트요", "가우디 대표작. 외관과 내부 모두 환상적"),
            ("⛪", "고딕 지구", "중세 골목길·대성당·피카소 박물관"),
        ],
        "tips": [
            "사그라다 파밀리아는 반드시 온라인 사전 예매 (현장 매진 빈번)",
            "택시보다 공항버스(Aerobus)·지하철이 경제적",
            "람블라스 거리 소매치기 주의 — 카메라·지갑 관리 필수",
            "크루즈 승선 전날 바르셀로나 1박 추천 (지연 리스크 방지)",
            "탑승·하선 항구: Barcelona Cruise Port (World Trade Center 인근)",
        ],
        "destination_slug": "mediterranean",
    },
    "civitavecchia": {
        "nameKo": "치비타베키아 (로마 기항지)",
        "nameEn": "Civitavecchia",
        "country": "이탈리아",
        "emoji": "🇮🇹",
        "region": "지중해",
        "cover": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1200&q=80",
        "intro": """치비타베키아(Civitavecchia)는 로마(Roma)의 관문 항구입니다. 로마 시내에서 약 80km 거리에 위치하며, 크루즈 기항 시 대부분의 승객이 로마 시내 투어를 선택합니다. 항구에서 로마까지 기차로 약 1시간 15분, 셔틀버스로 약 1시간 30분 소요됩니다.

로마는 '영원의 도시'로 불리며, 콜로세움, 트레비 분수, 바티칸, 판테온 등 고대 로마와 르네상스 시대 유적이 가득합니다. 크루즈 기항 시간(보통 8~10시간)에 하이라이트를 효율적으로 돌 수 있습니다.

치비타베키아 항구 자체도 고대 로마 항구의 흔적과 미켈란젤로가 설계한 요새(Fort Michelangelo)가 있어 잠깐 산책하기 좋습니다.""",
        "highlights": [
            ("🏟️", "콜로세움", "서기 80년 완공, 수용 인원 5만 명. 사전 예매 필수"),
            ("⛲", "트레비 분수", "로마 최고 인기 명소. 동전 던지면 다시 온다는 전설"),
            ("🕍", "바티칸·성 베드로 대성당", "세계 최소 독립국, 미켈란젤로 천장화 시스티나 성당"),
            ("🏛️", "판테온", "무료 입장 (사전 예약 권장), 2,000년 된 로마 신전"),
            ("🌸", "스페인 광장", "오드리 헵번 '로마의 휴일' 촬영지, 137계단"),
            ("🍕", "로마 피자·파스타", "진짜 탄산수 없이 먹는 로마식 피자 알 탈리오"),
        ],
        "tips": [
            "콜로세움+포럼 입장권 사전 온라인 예매 필수 (현장 3~4시간 대기)",
            "치비타베키아→로마 기차: Civitavecchia역 출발, Roma Termini 도착, 편도 약 €4~6",
            "크루즈 선사 공식 로마 투어보다 개인 투어가 저렴하고 유연",
            "바티칸은 별도 예약 필요, 성 베드로 대성당 반바지·민소매 입장 불가",
            "복귀 시간 여유 있게 확보 (기차 지연 가능성)",
        ],
        "destination_slug": "mediterranean",
    },
    "naples": {
        "nameKo": "나폴리",
        "nameEn": "Naples",
        "country": "이탈리아",
        "emoji": "🇮🇹",
        "region": "지중해",
        "cover": "https://images.unsplash.com/photo-1534113414509-0eec2bfb493f?w=1200&q=80",
        "intro": """나폴리(Naples, Napoli)는 이탈리아 남부의 대표 항구 도시입니다. 크루즈 기항지로는 나폴리 항구(Port of Naples)를 거점으로 폼페이, 카프리 섬, 소렌토, 아말피 해안 등 세계적인 명소로의 당일 투어가 가능합니다.

나폴리는 피자의 발상지이기도 합니다. 특히 '마르게리타 피자'는 나폴리 퀸 마르게리타를 위해 1889년 처음 만들어졌으며, 유네스코 무형문화유산으로 등재된 나폴리탄 피자를 맛보는 것은 필수 코스입니다.

나폴리 항구 뒤로 보이는 베수비오 화산은 서기 79년 폼페이를 덮은 바로 그 화산으로, 지금도 활화산으로 분류됩니다.""",
        "highlights": [
            ("🌋", "폼페이 유적", "서기 79년 화산재에 덮인 로마 도시 유적, UNESCO 세계유산"),
            ("🏝️", "카프리 섬", "지중해 최고의 섬, 블루 그로토(푸른 동굴)·빌라 조비스"),
            ("🍋", "소렌토", "레몬 향 가득한 절벽 마을, 아말피 코스트 시작점"),
            ("🌊", "아말피 해안", "유네스코 세계유산, 절벽 드라이브·파스텔 마을"),
            ("🍕", "나폴리 피자", "원조 나폴리탄 피자, L'Antica Pizzeria da Michele (영화 속 그 가게)"),
            ("🏰", "카스텔 누오보", "나폴리 항구 바로 옆 중세 성, 무료 입장"),
        ],
        "tips": [
            "폼페이는 나폴리에서 기차 40분 (Circumvesuviana 노선)",
            "카프리 섬은 페리 50분. 블루 그로토는 날씨·파도에 따라 입장 불가 가능",
            "나폴리 시내 소매치기·오토바이 날치기 주의 (가방 앞으로 메기)",
            "폼페이 입장권 사전 예매 권장 (여름 성수기 현장 대기 김)",
            "크루즈 기항 시간이 짧으면 폼페이 OR 카프리 중 하나 선택 권장",
        ],
        "destination_slug": "mediterranean",
    },
    "athens": {
        "nameKo": "아테네 (피레우스 항)",
        "nameEn": "Athens / Piraeus",
        "country": "그리스",
        "emoji": "🇬🇷",
        "region": "지중해",
        "cover": "https://images.unsplash.com/photo-1555993539-1732b0258235?w=1200&q=80",
        "intro": """크루즈는 아테네 서쪽 피레우스(Piraeus) 항구에 입항합니다. 피레우스에서 아테네 시내까지는 지하철(Metro Line 1)로 약 25분, 택시로 약 30분 거리입니다.

아테네는 서구 문명의 발상지로, 2,500년 역사의 아크로폴리스와 파르테논 신전이 세계 각지의 관광객을 불러 모읍니다. 고대 아고라, 제우스 신전, 국립 고고학 박물관 등 유적지가 밀집해 있어 반나절만으로도 하이라이트를 볼 수 있습니다.

아테네에서 페리를 타면 산토리니, 미코노스, 로도스 등 에게해 섬으로 이동할 수 있어 크루즈 기항 전후 섬 여행을 계획하는 분들에게도 좋은 거점입니다.""",
        "highlights": [
            ("🏛️", "아크로폴리스·파르테논 신전", "기원전 447년 건립, 아테네의 상징"),
            ("🏺", "아크로폴리스 박물관", "파르테논 조각품 원본 전시, 세계 최고 수준"),
            ("🏟️", "고대 아고라", "소크라테스가 철학을 논하던 고대 광장"),
            ("🌿", "플라카 지구", "아크로폴리스 아래 그리스 전통 골목, 타베르나 밀집"),
            ("🏛️", "제우스 신전", "거대한 코린트식 기둥이 인상적인 제우스 신전"),
            ("🛍️", "모나스티라키 시장", "벼룩시장·기념품·그리스 간식 총집합"),
        ],
        "tips": [
            "아크로폴리스 입장권은 복합 티켓(6개 유적지 포함) 구매 추천",
            "7~8월 아테네는 40도에 육박 — 모자·물·자외선 차단제 필수",
            "피레우스→아테네 Metro Line 1: Piraeus역 승차, Monastiraki역 하차",
            "산토리니·미코노스 크루즈 기항 시 텐더 보트 이용 (시간 추가 소요)",
            "그리스 음식: 수블라키, 무사카, 호리아티키(그리스 샐러드) 추천",
        ],
        "destination_slug": "mediterranean",
    },
    "santorini": {
        "nameKo": "산토리니",
        "nameEn": "Santorini",
        "country": "그리스",
        "emoji": "🇬🇷",
        "region": "지중해",
        "cover": "https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?w=1200&q=80",
        "intro": """산토리니(Santorini)는 에게해에 위치한 그리스의 화산섬으로, 흰색 건물과 파란 지붕이 절벽 위에 펼쳐지는 풍경으로 세계에서 가장 아름다운 섬 중 하나로 꼽힙니다. 수천 년 전 화산 폭발로 형성된 칼데라 지형이 독특한 풍경을 만들어냅니다.

크루즈 기항 시 산토리니에는 항구(Athinios Port)나 피라(Fira) 앞바다에 닻을 내리고 텐더 보트로 해안에 접안합니다. 피라 시내로는 케이블카 또는 당나귀를 타고 올라갈 수 있습니다.

이아(Oia) 마을의 석양은 세계 10대 석양 중 하나로 선정될 만큼 유명하지만, 크루즈 기항 시간에는 보기 어려울 수 있으므로 일정 확인이 필요합니다.""",
        "highlights": [
            ("🌅", "이아(Oia) 마을", "세계 최고 석양, 파란 지붕·하얀 벽 사진 명소"),
            ("🏙️", "피라(Fira) 시내", "케이블카로 연결되는 칼데라 뷰 카페·레스토랑"),
            ("🌋", "네아 카메니 화산", "선착장에서 보트로 30분, 활화산 트레킹"),
            ("🏖️", "레드 비치·페리사 해변", "화산 지형 독특한 검은 모래 해변"),
            ("🍷", "산토리니 와인", "화산토에서 자란 어시르티코(Assyrtiko) 화이트 와인 유명"),
            ("📸", "피라↔이아 트레킹", "10km 절벽 트레킹, 칼데라 뷰 장관"),
        ],
        "tips": [
            "텐더 보트 탑승 시간 포함해 기항지 시간 계산 (왕복 30~40분 추가)",
            "케이블카 대기 길면 당나귀 이동 가능 (인도적 논란 있음, 도보도 가능)",
            "여름 성수기(7~8월) 매우 혼잡 — 이아는 이른 아침 방문 권장",
            "크루즈 기항지에서 이아까지 버스 또는 택시 이동",
            "ATV 렌트로 섬 일주 가능 (약 €30~50/일)",
        ],
        "destination_slug": "mediterranean",
    },
    "dubrovnik": {
        "nameKo": "두브로브니크",
        "nameEn": "Dubrovnik",
        "country": "크로아티아",
        "emoji": "🇭🇷",
        "region": "지중해",
        "cover": "https://images.unsplash.com/photo-1548777123-e216912df7d8?w=1200&q=80",
        "intro": """두브로브니크(Dubrovnik)는 크로아티아 남부 아드리아해 연안의 도시로, '아드리아해의 진주'라고 불립니다. 중세 성벽으로 둘러싸인 구시가지(Old Town)는 유네스코 세계문화유산으로 지정되어 있으며, HBO 드라마 '왕좌의 게임'(Game of Thrones)의 킹스랜딩으로도 유명합니다.

두브로브니크 크루즈 항구는 구시가지에서 약 3km 거리에 위치합니다. 버스 또는 택시로 약 10분이면 구시가지 필레(Pile) 게이트에 도착할 수 있습니다.

성벽 투어(City Walls)는 두브로브니크 방문의 하이라이트입니다. 약 2km 성벽을 걸으며 오렌지빛 지붕과 푸른 아드리아해의 전망을 감상할 수 있습니다.""",
        "highlights": [
            ("🏰", "두브로브니크 성벽", "2km 성벽 투어, 최고의 파노라마 뷰"),
            ("⛵", "왕좌의 게임 투어", "킹스랜딩 촬영지 투어, 팬들에게 필수"),
            ("🚡", "스르지 산 케이블카", "구시가지 전망 케이블카, 정상에서 어드리아해 조망"),
            ("🏖️", "반예 해변", "구시가지 바로 옆 크리스털 바다 해변"),
            ("🛍️", "플라자(Placa) 거리", "구시가지 중앙 대리석 거리, 카페·쇼핑"),
            ("⛵", "로크룸 섬 페리", "구시가지에서 페리 15분, 자연보호구역 섬"),
        ],
        "tips": [
            "크루즈 성수기(여름)에는 하루 7~8척 크루즈 동시 정박 — 매우 혼잡",
            "구시가지 입장료·성벽 입장료 별도 (합산 약 €35~40)",
            "오전 8~9시 도착 시 혼잡 최소화 가능",
            "두브로브니크 카드(버스·케이블카 포함) 구매 시 절약 가능",
            "구시가지 내 레스토랑보다 골목 안 로컬 식당이 저렴",
        ],
        "destination_slug": "mediterranean",
    },
    "tokyo": {
        "nameKo": "도쿄 (요코하마 항)",
        "nameEn": "Tokyo / Yokohama",
        "country": "일본",
        "emoji": "🇯🇵",
        "region": "아시아",
        "cover": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1200&q=80",
        "intro": """도쿄(Tokyo)의 크루즈 기항지는 요코하마 항(Port of Yokohama)과 도쿄 국제 크루즈 터미널(Harumi Pier)이 주로 사용됩니다. MSC 벨리시마 등 아시아 크루즈 노선의 주요 출발·도착 항입니다.

요코하마에서 도쿄 시내(신주쿠·시부야 등)까지는 JR 요코하마선·JR 게이힌토호쿠선으로 약 40~50분이면 접근 가능합니다. 요코하마 자체도 차이나타운, 미나토미라이 21(未来みなとみらい21), 산케이엔 정원 등 볼거리가 풍부합니다.

일본은 한국에서 가장 접근성이 좋은 국외 크루즈 목적지로, 한국 출발 크루즈의 주요 기항지이기도 합니다.""",
        "highlights": [
            ("⛩️", "아사쿠사·센소지", "도쿄 최고 전통 사원, 나카미세 거리 쇼핑"),
            ("🗼", "도쿄 스카이트리", "634m 세계 최고 수준 전망대"),
            ("🍜", "신주쿠·시부야", "도쿄 최대 번화가, 스크램블 교차로"),
            ("🏯", "황궁·황궁 동쪽 정원", "에도성 터, 무료 입장"),
            ("🛍️", "하라주쿠·오모테산도", "패션·카페 거리, 명품·트렌드 쇼핑"),
            ("🎡", "요코하마 미나토미라이", "야경 명소, 대관람차·코스모월드"),
        ],
        "tips": [
            "IC카드(Suica/PASMO) 구매 시 JR·버스·지하철 모두 사용 가능",
            "도쿄는 1일 교통비 €10~15 수준, 지하철이 저렴하고 정확",
            "기항지 시간 8~10시간이면 아사쿠사+신주쿠+도쿄타워 코스 가능",
            "항구→시내 택시 비쌈 — 버스·전철 이용 추천",
            "IC카드는 편의점(세븐일레븐·로손)에서도 결제 가능",
            "식당 영어 메뉴 제한적 — 음식 사진 메뉴 또는 번역 앱 활용",
        ],
        "destination_slug": "japan",
    },
    "busan": {
        "nameKo": "부산",
        "nameEn": "Busan",
        "country": "한국",
        "emoji": "🇰🇷",
        "region": "아시아",
        "cover": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1200&q=80",
        "intro": """부산(釜山)은 한국 제2의 도시이자 최대 항구 도시입니다. MSC 벨리시마 등 아시아 크루즈 노선에서 한국 기항지로 많이 선택되며, 한국 출발 크루즈의 승선 항구로도 활용됩니다.

부산항 국제여객터미널은 부산 도심(중구)에 위치해 도시 접근성이 뛰어납니다. 터미널에서 남포동, 자갈치 시장까지 도보로 이동 가능하며, 해운대·광안리 해수욕장까지는 지하철로 20~30분입니다.

부산은 해산물 천국입니다. 자갈치 시장의 신선한 회, 밀면, 돼지국밥 등 부산 특유의 음식 문화를 외국 크루즈 승객들도 즐겨 찾습니다.""",
        "highlights": [
            ("🌊", "해운대·광안리 해수욕장", "한국 대표 해변, 광안대교 야경 명소"),
            ("🐟", "자갈치 시장", "부산 최대 수산물 시장, 신선회·해산물 직판"),
            ("🏯", "용두산 공원·부산타워", "원도심 전망, 부산타워 야경"),
            ("🎨", "감천문화마을", "'한국의 산토리니' 벽화 마을, 인스타 명소"),
            ("🌿", "태종대", "절벽·등대·유람선, 부산 남단 자연 명소"),
            ("🏖️", "송정해수욕장", "해운대보다 한적한 서핑 비치"),
        ],
        "tips": [
            "부산 지하철 1일권 €3 내외, 주요 관광지 모두 연결",
            "자갈치→남포동→용두산→국제시장 도보 코스 추천",
            "감천문화마을은 조용한 주거지, 주민 배려 관광 요청",
            "해운대 근처 기장시장 랍스터·대게 저렴하게 즐길 수 있음",
            "크루즈 기항 시간이 저녁까지면 광안대교 야경 추천",
        ],
        "destination_slug": "korea",
    },
    "jeju": {
        "nameKo": "제주",
        "nameEn": "Jeju",
        "country": "한국",
        "emoji": "🇰🇷",
        "region": "아시아",
        "cover": "https://images.unsplash.com/photo-1469796466635-455ede028aca?w=1200&q=80",
        "intro": """제주도(Jeju Island)는 한국의 최남단 화산섬으로, 유네스코 세계자연유산·생물권보전지역·세계지질공원으로 지정된 자연의 보고입니다. MSC 벨리시마 아시아 크루즈 노선의 한국 기항지로 점점 주목받고 있습니다.

제주 외항(제주항 국제여객터미널)에 크루즈가 정박하며, 시내 관광지까지 택시·버스로 쉽게 이동할 수 있습니다. 제주의 대표 자연 명소인 한라산(1,950m), 만장굴, 성산일출봉은 기항 하루로 하이라이트를 충분히 즐길 수 있습니다.

제주는 외국 관광객에게 '한국의 하와이'로 알려져 있으며, 독특한 제주 방언, 해녀 문화, 흑돼지 요리 등 독자적인 문화를 가지고 있습니다.""",
        "highlights": [
            ("🌋", "성산일출봉", "유네스코 세계유산, 일출 명소, 해녀 공연"),
            ("🕳️", "만장굴", "유네스코 세계유산, 세계 최대 규모 용암 동굴"),
            ("🌊", "협재·함덕 해수욕장", "에메랄드 바다, 스노클링·수상스포츠"),
            ("🐖", "제주 흑돼지", "제주 전통 흑돼지 구이, 필수 체험"),
            ("🌿", "사려니숲길", "제주의 숲 트레킹, 치유의 숲"),
            ("🍊", "제주 감귤 체험", "제주 감귤·한라봉 직접 따기 체험"),
        ],
        "tips": [
            "크루즈 기항 시간 짧으면 성산일출봉 OR 만장굴 중 선택 권장",
            "렌터카 이용 시 하루에 주요 명소 5~6곳 가능",
            "제주 버스 편리하지만 배차 간격 길어 택시 병용 권장",
            "성산일출봉 해녀 공연: 10:30, 13:00, 14:30 (날씨 영향)",
            "제주도 면세 쇼핑 — 화장품·주류·식품 인기",
        ],
        "destination_slug": "korea",
    },
    "singapore": {
        "nameKo": "싱가포르",
        "nameEn": "Singapore",
        "country": "싱가포르",
        "emoji": "🇸🇬",
        "region": "아시아",
        "cover": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=1200&q=80",
        "intro": """싱가포르(Singapore)는 동남아시아 크루즈의 핵심 허브 항구입니다. 마리나 베이 크루즈 센터(Marina Bay Cruise Centre)와 탄종파가 크루즈 센터(Tanah Merah Ferry Terminal)가 주요 크루즈 항구로 사용됩니다.

싱가포르는 크루즈 기항지 중 가장 편리한 도시 중 하나입니다. 대중교통(MRT)이 완벽하게 구축되어 있고, 영어가 공용어여서 외국인 관광객도 쉽게 이동할 수 있습니다.

가든스 바이 더 베이의 슈퍼트리, 마리나 베이 샌즈 인피니티풀(투숙객만), 센토사 섬의 유니버설 스튜디오, 차이나타운·리틀 인디아 등 다양한 문화권이 공존하는 도시입니다.""",
        "highlights": [
            ("🌳", "가든스 바이 더 베이", "슈퍼트리 야경, 플라워돔·클라우드포레스트 온실"),
            ("🏨", "마리나 베이 샌즈", "세계적 랜드마크, 스카이파크 전망대 입장 가능"),
            ("🎢", "유니버설 스튜디오 싱가포르", "센토사 섬, 하루 즐기기 좋은 테마파크"),
            ("🦁", "싱가포르 동물원·나이트 사파리", "야간 사파리 세계 최고 수준"),
            ("🛍️", "오차드 로드", "싱가포르 최대 쇼핑 거리"),
            ("🍜", "홍림 푸드 센터", "칠리크랩·호커 음식 저렴하게 즐기는 로컬 푸드코트"),
        ],
        "tips": [
            "MRT 1회권 약 SGD 1.5~2 / EZ-Link 카드 구매 추천",
            "싱가포르 날씨 연중 30~35도 — 자외선 차단제 필수",
            "껌 반입·무단 횡단·흡연 구역 외 흡연 엄격히 금지",
            "호커 센터(Hawker Centre) 음식 SGD 4~8, 맛있고 저렴",
            "센토사 섬은 모노레일·버스로 이동 가능",
        ],
        "destination_slug": "asia",
    },
    "juneau": {
        "nameKo": "주노 (알래스카)",
        "nameEn": "Juneau, Alaska",
        "country": "미국",
        "emoji": "🇺🇸",
        "region": "알래스카",
        "cover": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=1200&q=80",
        "intro": """주노(Juneau)는 미국 알래스카 주의 주도(州都)이자 알래스카 크루즈의 핵심 기항지입니다. 주노는 도로로 연결되지 않은 도시로, 크루즈와 항공편만으로 접근할 수 있는 독특한 도시입니다.

주노 최대의 볼거리는 멘덴홀 빙하(Mendenhall Glacier)입니다. 크루즈 터미널에서 셔틀버스로 약 20분 거리에 위치한 이 빙하는 약 12마일 길이로, 가까이서 빙하의 웅장함을 직접 볼 수 있습니다. 단, 지구 온난화로 매년 빙하가 후퇴하고 있어 지금 방문하는 것이 더욱 의미 있습니다.

여름 시즌(5~9월)에는 험발 고래(Humpback Whale) 관찰 투어도 인기입니다. 주노 앞바다에서 혹등고래의 점프를 목격할 수 있는 확률이 높습니다.""",
        "highlights": [
            ("🧊", "멘덴홀 빙하", "알래스카 대표 빙하, 빙하 트레킹 투어 가능"),
            ("🐋", "고래 관찰 투어", "험발 고래 점프 목격 확률 90% 이상 (여름)"),
            ("🚁", "빙하 헬기 투어", "헬기 타고 빙하 위 착지, 짜릿한 경험"),
            ("🦅", "독수리 관찰", "주노 시내 가로등·나무에서 흰머리독수리 상시 목격"),
            ("🎣", "연어 낚시", "알래스카 연어 직접 낚는 체험 투어"),
            ("🍺", "주노 지역 맥주", "Devil's Club Brewing 등 로컬 브루어리 탐방"),
        ],
        "tips": [
            "멘덴홀 빙하 왕복 셔틀+입장료 약 USD 35~45",
            "고래 관찰 투어 약 3시간, USD 120~160 (크루즈 공식 투어보다 현지 예약 저렴)",
            "날씨 변화 심함 — 방수 재킷 필수",
            "6~8월 비 많고 기온 10~15도, 여름이지만 얇은 패딩 준비",
            "크루즈 기항 시간 6~8시간 — 멘덴홀 빙하 + 다운타운 조합 추천",
        ],
        "destination_slug": "alaska",
    },
}

# ──────────────────────────────────────────
# CSS (공통)
# ──────────────────────────────────────────
def guide_css():
    return """<style>
    .g-hero{position:relative;height:420px;overflow:hidden;display:flex;align-items:flex-end}
    .g-hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
    .g-hero-overlay{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.75) 0%,rgba(0,0,0,.1) 60%)}
    .g-hero-content{position:relative;z-index:1;width:100%;padding:36px 0;color:#fff}
    .breadcrumb{font-size:.82rem;color:rgba(255,255,255,.75);margin-bottom:10px}
    .breadcrumb a{color:rgba(255,255,255,.75);text-decoration:none}
    .g-hero h1{font-size:2rem;font-weight:900;margin:0 0 10px;line-height:1.2}
    .g-hero-meta{display:flex;gap:10px;flex-wrap:wrap;font-size:.85rem;opacity:.9}
    .g-hero-meta span{background:rgba(255,255,255,.15);padding:3px 10px;border-radius:20px;backdrop-filter:blur(4px)}
    .g-layout{display:grid;grid-template-columns:1fr 300px;gap:36px;max-width:1200px;margin:44px auto;padding:0 20px;align-items:start}
    @media(max-width:900px){.g-layout{grid-template-columns:1fr}.g-hero h1{font-size:1.5rem}}
    .g-body h2{font-size:1.3rem;font-weight:900;color:#1a237e;margin:36px 0 14px;padding-bottom:8px;border-bottom:3px solid #ff6f00;display:inline-block}
    .g-body h3{font-size:1.05rem;font-weight:700;color:#1a237e;margin:20px 0 8px}
    .g-body p{color:#616161;line-height:1.9;margin-bottom:14px}
    .g-body ul{padding-left:20px;color:#616161;line-height:2;margin-bottom:14px}
    .hl-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:16px 0}
    @media(max-width:600px){.hl-grid{grid-template-columns:repeat(2,1fr)}}
    .hl-card{background:#fafafa;border-radius:8px;padding:14px;border-left:3px solid #ff6f00}
    .hl-card .icon{font-size:1.5rem;margin-bottom:6px}
    .hl-card .name{font-size:.88rem;font-weight:700;color:#1a237e}
    .hl-card .desc{font-size:.78rem;color:#9e9e9e;margin-top:3px;line-height:1.5}
    .tip-list{background:#fff8e1;border-radius:8px;padding:16px 20px;margin:16px 0}
    .tip-list li{font-size:.88rem;color:#616161;line-height:1.9}
    .sidebar-card{background:#fff;border:1px solid #eeeeee;border-radius:8px;padding:20px;margin-bottom:18px;box-shadow:0 2px 8px rgba(0,0,0,.1)}
    .sidebar-card h3{font-size:.95rem;font-weight:700;color:#1a237e;margin:0 0 14px;padding-bottom:8px;border-bottom:2px solid #eeeeee}
    .cta-btn{display:block;background:#ff6f00;color:#fff;text-align:center;padding:13px;border-radius:8px;font-weight:700;font-size:.92rem;text-decoration:none;margin-top:8px;transition:background .2s}
    .cta-btn:hover{background:#e65100}
    .cta-btn.navy{background:#1a237e}
    .cta-btn.navy:hover{background:#0d1642}
    h2[id],h3[id]{scroll-margin-top:80px}
    .g-sidebar{position:sticky;top:80px}
    .nearby-port{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid #eeeeee;font-size:.85rem;text-decoration:none;color:#616161}
    .nearby-port:last-child{border-bottom:none}
    .nearby-port:hover{color:#1a237e}
  </style>"""

# ──────────────────────────────────────────
# 기항지 페이지 생성
# ──────────────────────────────────────────
def make_port_page(slug, p):
    nameKo = p["nameKo"]
    nameEn = p["nameEn"]
    country = p["country"]
    emoji = p["emoji"]
    region = p["region"]
    cover = p["cover"]
    intro = p["intro"]
    highlights = p["highlights"]
    tips = p["tips"]

    title = f"{nameKo} 크루즈 기항지 가이드 2026 | 볼거리·투어·팁 총정리 - 크루즈링크"
    desc = f"{nameKo}({nameEn}) 크루즈 기항지 완벽 가이드. 주요 볼거리, 추천 투어, 이동 방법, 현지 팁까지 크루즈링크가 정리합니다."
    keywords = f"{nameKo}, {nameEn}, 크루즈 기항지, {region} 크루즈, 크루즈 투어"

    hl_cards = "".join(f"""
        <div class="hl-card">
          <div class="icon">{ic}</div>
          <div class="name">{html.escape(name)}</div>
          <div class="desc">{html.escape(desc_)}</div>
        </div>""" for ic, name, desc_ in highlights)

    tip_items = "".join(f"<li>{html.escape(t)}</li>" for t in tips)

    # 관련 기항지 링크
    related = [(k, v) for k, v in PORTS.items() if k != slug and v["region"] == region][:4]
    related_links = "".join(f"""
        <a class="nearby-port" href="{k}.html">{v['emoji']} {html.escape(v['nameKo'])}</a>""" for k, v in related)

    dots = "../../"
    intro_paras = "".join(f"<p>{html.escape(para.strip())}</p>" for para in intro.split("\n\n") if para.strip())

    page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="keywords" content="{html.escape(keywords)}">
  <link rel="canonical" href="https://www.cruiselink.co.kr/guide/ports/{slug}.html">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="크루즈링크">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:image" content="{cover}">
  <meta property="og:url" content="https://www.cruiselink.co.kr/guide/ports/{slug}.html">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap">
  <link rel="stylesheet" href="{dots}assets/css/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚢</text></svg>">
  {guide_css()}
</head>
<body>
<div id="header"></div>

<section class="g-hero">
  <img src="{cover}" alt="{html.escape(nameKo)}" loading="eager">
  <div class="g-hero-overlay"></div>
  <div class="g-hero-content">
    <div class="container">
      <div class="breadcrumb"><a href="{dots}">홈</a> › <a href="../">가이드</a> › <a href="./">기항지 정보</a> › {html.escape(nameKo)}</div>
      <h1>{emoji} {html.escape(nameKo)} 기항지 가이드</h1>
      <div class="g-hero-meta">
        <span>🌍 {html.escape(country)}</span>
        <span>🚢 {html.escape(region)} 크루즈 기항지</span>
        <span>✈️ 크루즈 기항 시 볼거리 총정리</span>
      </div>
    </div>
  </div>
</section>

<div class="g-layout">
  <article class="g-body">

    <h2 id="intro">{html.escape(nameKo)} 소개</h2>
    {intro_paras}

    <h2 id="highlights">주요 볼거리 & 명소</h2>
    <div class="hl-grid">{hl_cards}</div>

    <h2 id="tips">크루즈 기항지 실전 팁</h2>
    <ul class="tip-list">{tip_items}</ul>

    <h2 id="cruise">이 기항지를 포함한 크루즈 찾기</h2>
    <p>{html.escape(nameKo)}을(를) 기항하는 크루즈 상품은 크루즈링크에서 검색하실 수 있습니다. 전문 상담원이 최적의 노선과 일정을 안내해 드립니다.</p>

  </article>

  <aside class="g-sidebar">
    <div class="sidebar-card">
      <h3>📋 목차</h3>
      <ul style="list-style:none;padding:0;margin:0">
        <li style="margin-bottom:2px"><a href="#intro" style="font-size:.85rem;color:#616161;text-decoration:none;padding:4px 8px;display:block;border-radius:4px" onmouseover="this.style.background='#f5f5f5'" onmouseout="this.style.background=''">지역 소개</a></li>
        <li style="margin-bottom:2px"><a href="#highlights" style="font-size:.85rem;color:#616161;text-decoration:none;padding:4px 8px;display:block;border-radius:4px" onmouseover="this.style.background='#f5f5f5'" onmouseout="this.style.background=''">주요 볼거리</a></li>
        <li style="margin-bottom:2px"><a href="#tips" style="font-size:.85rem;color:#616161;text-decoration:none;padding:4px 8px;display:block;border-radius:4px" onmouseover="this.style.background='#f5f5f5'" onmouseout="this.style.background=''">실전 팁</a></li>
        <li style="margin-bottom:2px"><a href="#cruise" style="font-size:.85rem;color:#616161;text-decoration:none;padding:4px 8px;display:block;border-radius:4px" onmouseover="this.style.background='#f5f5f5'" onmouseout="this.style.background=''">크루즈 찾기</a></li>
      </ul>
    </div>
    <div class="sidebar-card">
      <h3>🚢 이 기항지 크루즈 예약</h3>
      <p style="font-size:.83rem;color:#616161;margin-bottom:4px">{html.escape(nameKo)} 기항 크루즈를 찾아보세요.</p>
      <a class="cta-btn" href="{dots}search.html">크루즈 검색</a>
      <a class="cta-btn navy" href="{dots}#inquiry">무료 상담 신청</a>
    </div>
    {f'''<div class="sidebar-card">
      <h3>🌍 {html.escape(region)} 다른 기항지</h3>
      {related_links}
    </div>''' if related_links else ''}
  </aside>
</div>

<div id="footer"></div>
<script src="{dots}assets/data/translations.js"></script>
<script src="{dots}assets/js/api.js"></script>
<script src="{dots}assets/js/components.js"></script>
<script>
  document.getElementById('header').innerHTML = Components.header('{dots}');
  document.getElementById('footer').innerHTML = Components.footer('{dots}');
</script>
</body></html>"""
    return page

# ──────────────────────────────────────────
# 기항지 인덱스
# ──────────────────────────────────────────
def make_ports_index():
    by_region = {}
    for slug, p in PORTS.items():
        r = p["region"]
        by_region.setdefault(r, []).append((slug, p))

    sections = ""
    for region, ports in by_region.items():
        cards = "".join(f"""
        <a href="{slug}.html" style="background:#fff;border:1px solid #eeeeee;border-radius:8px;overflow:hidden;text-decoration:none;display:block;color:inherit;transition:box-shadow .2s" onmouseover="this.style.boxShadow='0 4px 20px rgba(0,0,0,.12)'" onmouseout="this.style.boxShadow='none'">
          <img src="{p['cover']}" alt="{html.escape(p['nameKo'])}" style="width:100%;height:140px;object-fit:cover" loading="lazy">
          <div style="padding:14px">
            <div style="font-size:1.1rem">{p['emoji']}</div>
            <div style="font-weight:700;color:#1a237e;margin-top:4px">{html.escape(p['nameKo'])}</div>
            <div style="font-size:.8rem;color:#9e9e9e;margin-top:2px">{html.escape(p['country'])}</div>
          </div>
        </a>""" for slug, p in ports)

        sections += f"""
      <section style="margin-bottom:48px">
        <h2 style="font-size:1.3rem;font-weight:900;color:#1a237e;margin-bottom:8px">🌍 {html.escape(region)}</h2>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px">
          {cards}
        </div>
      </section>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>크루즈 기항지 가이드 | 지중해·아시아·알래스카 - 크루즈링크</title>
  <meta name="description" content="크루즈 기항지별 볼거리, 투어, 실전 팁 완벽 가이드. 지중해(바르셀로나, 로마, 산토리니), 아시아(도쿄, 부산, 싱가포르), 알래스카 등.">
  <link rel="canonical" href="https://www.cruiselink.co.kr/guide/ports/">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap">
  <link rel="stylesheet" href="../../assets/css/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚢</text></svg>">
</head>
<body>
<div id="header"></div>
<section style="background:linear-gradient(135deg,#1a237e 0%,#283593 100%);color:#fff;padding:70px 0;text-align:center">
  <div class="container">
    <h1 style="font-size:2rem;font-weight:900;margin:0 0 10px">🌍 크루즈 기항지 가이드</h1>
    <p style="opacity:.85;margin:0">기항지별 볼거리·투어·실전 팁을 크루즈링크가 정리합니다</p>
  </div>
</section>
<div class="container" style="padding:44px 20px">{sections}</div>
<div id="footer"></div>
<script src="../../assets/data/translations.js"></script>
<script src="../../assets/js/api.js"></script>
<script src="../../assets/js/components.js"></script>
<script>
  document.getElementById('header').innerHTML = Components.header('../../');
  document.getElementById('footer').innerHTML = Components.footer('../../');
</script>
</body></html>"""

# ──────────────────────────────────────────
# 실행
# ──────────────────────────────────────────
print("=== 기항지 가이드 생성 ===")

with open(OUT / "ports" / "index.html", "w", encoding="utf-8") as f:
    f.write(make_ports_index())
print("✅ guide/ports/index.html")

for slug, p in PORTS.items():
    page = make_port_page(slug, p)
    with open(OUT / "ports" / f"{slug}.html", "w", encoding="utf-8") as f:
        f.write(page)
    print(f"  ✅ ports/{slug}.html — {p['nameKo']}")

print(f"\n🎉 기항지 페이지 {len(PORTS) + 1}개 생성 완료!")
