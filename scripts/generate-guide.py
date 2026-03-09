#!/usr/bin/env python3
"""
CruiseLink Guide Page Generator
선사 소개, 선박 소개 HTML 페이지 자동 생성
"""
import json, os, re, html
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
DATA = BASE / "assets/data"
OUT = BASE / "guide"

# 디렉토리 생성
for d in ["cruise-lines", "ships", "ports", "tours"]:
    (OUT / d).mkdir(parents=True, exist_ok=True)

# 데이터 로드
with open(DATA / "ships.json", encoding="utf-8") as f:
    ships = json.load(f)
with open(DATA / "ships-detail.json", encoding="utf-8") as f:
    ships_detail = {s["slug"]: s for s in json.load(f)}
with open(DATA / "cruises.json", encoding="utf-8") as f:
    all_cruises = json.load(f)

# 선사별 선박 그룹핑
by_operator = defaultdict(list)
for s in ships:
    by_operator[s["operator"]].append(s)

# 선사별 크루즈 그룹핑
cruises_by_ship = defaultdict(list)
for c in all_cruises:
    cruises_by_ship[c.get("shipSlug","")].append(c)

# ──────────────────────────────────────────
# 선사 정보 (한국어 설명)
# ──────────────────────────────────────────
OPERATOR_INFO = {
    "MSC Cruises": {
        "slug": "msc-cruises",
        "nameKo": "MSC 크루즈",
        "emoji": "🇮🇹",
        "tagline": "지중해에서 태어난 세계 최대 크루즈 선사",
        "intro": """MSC 크루즈(MSC Cruises)는 1987년 이탈리아에서 설립된 세계 최대 규모의 크루즈 선사 중 하나입니다. 본사는 스위스 제네바에 위치하며, 전 세계 270개 이상의 기항지에 노선을 운영합니다. MSC는 지중해 특유의 우아함과 이탈리아 라이프스타일을 선상에서 그대로 재현해 전 세계 크루즈 여행자들에게 사랑받고 있습니다.

한국 시장에서 MSC 크루즈는 아시아 시즌 동안 MSC 벨리시마를 중심으로 도쿄, 부산, 제주, 상하이 등을 기항하는 노선을 운영하여 한국 승객의 현지 승선이 가능한 유일한 주요 크루즈 선사입니다.

MSC 크루즈의 가장 큰 특징은 다국적 승객을 위한 다양한 언어 서비스, 광범위한 다이닝 옵션, 그리고 어린이부터 어른까지 모든 연령층을 위한 엔터테인먼트 프로그램입니다. 특히 MSC Yacht Club이라는 선내 럭셔리 구역은 전용 레스토랑, 라운지, 버틀러 서비스를 제공해 프리미엄 경험을 원하는 승객에게 인기를 끌고 있습니다.""",
        "features": ["세계 최대 크루즈 선사 중 하나", "아시아 노선 한국 기항 (부산·제주)", "MSC Yacht Club 럭셔리 구역", "MSC for Me 스마트 기술", "지중해·알래스카·카리브 등 전 세계 운항"],
        "destinations": ["지중해", "아시아", "북유럽", "카리브해", "알래스카"],
        "cover": "https://assets.widgety.co.uk/2024/09/04/16/07/48/5bd29234-9b6c-4c86-b249-691473c4d907/MSC Cruises, MSC Bellissima, Exterior, Copyrights - MSC Rights.jpg",
    },
    "Norwegian Cruise Line": {
        "slug": "norwegian-cruise-line",
        "nameKo": "노르웨지안 크루즈 라인 (NCL)",
        "emoji": "🇺🇸",
        "tagline": "자유로운 크루즈 여행의 선구자, Freestyle Cruising",
        "intro": """노르웨지안 크루즈 라인(Norwegian Cruise Line, NCL)은 1966년 설립된 미국계 크루즈 선사로, 'Freestyle Cruising(자유로운 크루즈)'이라는 개념을 크루즈 업계에 처음 도입한 혁신적인 선사입니다. 기존 크루즈의 딱딱한 정해진 식사 시간과 드레스 코드를 없애고, 승객이 원하는 시간에 원하는 레스토랑에서 식사할 수 있는 자유로운 방식을 선보였습니다.

NCL은 알래스카 크루즈 시장에서 특히 강세를 보이며, 여름 시즌 알래스카 주력 선박들이 내부 항로(Inside Passage)를 운항합니다. 또한 하와이 크루즈를 운항하는 유일한 주요 선사로, Pride of America 호가 마우이, 힐로, 코나, 호놀룰루를 연결합니다.

NCL의 최신 선박들은 레이스트랙, 레이저 태그, 고카트 등 스릴 넘치는 시설을 갖추고 있어 가족 단위 여행객에게 매우 인기가 높습니다.""",
        "features": ["Freestyle Cruising — 자유로운 식사 시간", "알래스카 크루즈 최강자", "하와이 전용 선박 Pride of America", "레이스트랙·고카트 등 스릴 시설", "The Haven 럭셔리 구역"],
        "destinations": ["알래스카", "카리브해", "하와이", "지중해", "버뮤다"],
        "cover": "https://assets.widgety.co.uk/2024/05/29/09/13/44/8f5d5d2a-ae52-4ee1-81a4-f8d3e95d1b31/NCL Norwegian Prima - NCL.jpg",
    },
    "Explora Journeys": {
        "slug": "explora-journeys",
        "nameKo": "엑스플로라 저니스",
        "emoji": "✨",
        "tagline": "MSC 그룹의 울트라 럭셔리 크루즈 브랜드",
        "intro": """엑스플로라 저니스(Explora Journeys)는 MSC 그룹이 2023년 론칭한 울트라 럭셔리 크루즈 브랜드입니다. '오션 스테이트 오브 마인드(Ocean State of Mind)'를 콘셉트로, 최고급 승객 경험을 추구하는 여행자들을 위한 소규모 럭셔리 선박을 운영합니다.

엑스플로라 저니스의 가장 큰 특징은 승객 대 승무원 비율이 1.3:1에 달하는 압도적인 서비스 수준입니다. 객실의 모든 카테고리가 오션뷰이며, 발코니 또는 테라스가 기본 제공됩니다. 선내 레스토랑 9개, 바 12개 모두 포함(All-Inclusive)이며, 와인·스피릿까지 무제한 포함입니다.

2026년까지 총 5척의 선박(Explora I~V)을 순차 취항할 예정이며, 지중해, 북유럽, 카리브해 등 프리미엄 노선을 운항합니다. 크루즈링크에서는 한국 고객을 위한 엑스플로라 저니스 전담 상담 서비스를 제공합니다.""",
        "features": ["승객 대 승무원 1.3:1 최고급 서비스", "전 객실 오션뷰 + 발코니/테라스", "레스토랑·바 All-Inclusive (주류 포함)", "9개 레스토랑 / 12개 바", "MSC 그룹 산하 울트라 럭셔리"],
        "destinations": ["지중해", "북유럽", "카리브해", "중동", "동남아시아"],
        "cover": "https://assets.widgety.co.uk/2024/09/25/13/40/26/e94c8bd1-9cff-48a0-9ad6-d4b5de07fd11/Explora I - Exterior - Photo Credit Explora Journeys.jpg",
    },
    "Royal Caribbean International": {
        "slug": "royal-caribbean",
        "nameKo": "로열 캐리비안",
        "emoji": "👑",
        "tagline": "세계 최대 크루즈선 Icon of the Seas의 선사",
        "intro": """로열 캐리비안(Royal Caribbean International)은 1968년 설립된 세계 최대 크루즈 선사 중 하나로, 현재 전 세계에서 가장 많은 승객을 수송하는 선사입니다. 특히 세계 최대 크루즈선 아이콘 오브 더 시즈(Icon of the Seas)와 오아시스 클래스 선박들로 유명합니다.

로열 캐리비안은 '크루즈의 놀이공원'으로 불릴 만큼 스카이다이빙 시뮬레이터, 서핑 시뮬레이터, 암벽등반, 아이스링크, 실내 스카이다이빙 등 극한 액티비티를 선상에서 즐길 수 있습니다. 카리브해 전용 사설 섬 퍼펙트 데이(Perfect Day at CocoCay)도 운영하고 있습니다.""",
        "features": ["세계 최대 크루즈선 Icon of the Seas 운항", "서핑·스카이다이빙 등 극한 액티비티", "사설 섬 Perfect Day at CocoCay", "아이스링크·브로드웨이 쇼 완비", "전 세계 300개+ 기항지"],
        "destinations": ["카리브해", "지중해", "알래스카", "유럽", "아시아"],
        "cover": "https://assets.widgety.co.uk/2024/01/09/16/21/09/b695de21-a36d-4a97-aad4-a16bc8a12e64/Royal Caribbean International - Icon of the Seas - Aerial - SB.jpg",
    },
    "Celebrity Cruises": {
        "slug": "celebrity-cruises",
        "nameKo": "셀러브리티 크루즈",
        "emoji": "⭐",
        "tagline": "현대적 럭셔리 크루즈의 기준",
        "intro": """셀러브리티 크루즈(Celebrity Cruises)는 로열 캐리비안 그룹 산하의 프리미엄 크루즈 브랜드입니다. '모던 럭셔리(Modern Luxury)'를 콘셉트로 세련된 디자인, 미슐랭급 다이닝, 고급 스파 서비스를 제공합니다.

셀러브리티의 최신 Edge 시리즈 선박(Celebrity Edge, Celebrity Apex, Celebrity Beyond)은 혁신적인 Magic Carpet — 바다 위를 떠다니는 캔틸레버식 갑판 — 을 탑재해 화제를 모았습니다. 갈라파고스 군도, 아이슬란드 등 희귀한 목적지를 기항하는 특별 노선도 운영합니다.""",
        "features": ["Modern Luxury 프리미엄 포지셔닝", "Magic Carpet 혁신 갑판 구조", "미슐랭 영감 다이닝", "갈라파고스·아이슬란드 특별 노선", "로열 캐리비안 그룹 산하"],
        "destinations": ["지중해", "카리브해", "알래스카", "갈라파고스", "유럽"],
        "cover": "https://assets.widgety.co.uk/2022/04/06/09/13/41/eb0b8ffd-4d6b-4c93-897b-1f6b6d7fb571/Celebrity Beyond - Exterior - 2022 Celebrity Cruises.jpg",
    },
    "Carnival Cruise Line": {
        "slug": "carnival-cruise-line",
        "nameKo": "카니발 크루즈 라인",
        "emoji": "🎉",
        "tagline": "미국 최대 크루즈 선사, 즐거움과 가성비의 대명사",
        "intro": """카니발 크루즈 라인(Carnival Cruise Line)은 1972년 설립된 미국 최대 크루즈 선사입니다. '펀 십(Fun Ships)'이라는 별명처럼 파티 분위기, 다양한 엔터테인먼트, 합리적인 가격으로 미국 크루즈 시장을 석권하고 있습니다.

카니발은 플로리다, 텍사스, 캘리포니아 등 미국 다수의 항구에서 출발해 카리브해, 멕시코, 바하마 등을 잇는 단기 크루즈를 주로 운영합니다. 최근 출시한 카니발 마디 그라(Carnival Mardi Gras)는 미국 선사 중 최초로 선상 롤러코스터 BOLT를 탑재해 화제가 되었습니다.""",
        "features": ["미국 최대 크루즈 선사", "BOLT 선상 롤러코스터 (Mardi Gras)", "합리적인 가격 정책", "카리브해·멕시코 단기 노선 강세", "다양한 파티·엔터테인먼트"],
        "destinations": ["카리브해", "바하마", "멕시코", "버뮤다", "유럽"],
        "cover": "https://assets.widgety.co.uk/2022/01/12/14/43/48/2e8d9ca1-b174-4f11-819d-a68f4b9e85e5/Carnival Mardi Gras - Exterior - Carnival Cruise Line.jpg",
    },
    "Princess Cruises": {
        "slug": "princess-cruises",
        "nameKo": "프린세스 크루즈",
        "emoji": "👸",
        "tagline": "TV 시리즈 '러브 보트'의 그 선사",
        "intro": """프린세스 크루즈(Princess Cruises)는 1965년 설립되어 TV 시리즈 '러브 보트(The Love Boat)'로 전 세계에 알려진 크루즈 선사입니다. 현재 카니발 코퍼레이션 산하 브랜드로 운영되며, 알래스카 크루즈 시장에서 NCL과 함께 최강자로 꼽힙니다.

프린세스는 MedallionClass라는 독자적인 스마트 기술을 개발해 승선 시 스마트폰으로 모든 서비스를 컨트롤할 수 있습니다. 아시아 시장에서도 존재감이 크며, 다이아몬드 프린세스 등의 선박이 일본 및 동남아시아를 운항합니다.""",
        "features": ["'러브 보트' 원조 선사", "MedallionClass 스마트 기술", "알래스카 최강 노선", "아시아·일본 노선 운항", "카니발 코퍼레이션 산하"],
        "destinations": ["알래스카", "카리브해", "지중해", "아시아", "남태평양"],
        "cover": "https://assets.widgety.co.uk/2023/06/09/10/17/22/35c7b5b5-1e8e-4c42-b63e-7fee32f2e35a/Princess Cruises - Sun Princess - Exterior.jpg",
    },
    "Oceania Cruises": {
        "slug": "oceania-cruises",
        "nameKo": "오세아니아 크루즈",
        "emoji": "🌊",
        "tagline": "미식가를 위한 프리미엄 크루즈",
        "intro": """오세아니아 크루즈(Oceania Cruises)는 2002년 설립된 프리미엄 크루즈 선사로, '세계 최고의 크루즈 요리(The Finest Cuisine at Sea)'를 슬로건으로 내세울 만큼 다이닝에 특화되어 있습니다. 르 꼬르동 블루 출신 셰프들이 설계한 메뉴와 무료 특식 레스토랑이 업계 최고 수준으로 평가받습니다.

중·소형 선박(684~1,250명)을 운영해 대형 선박이 들어가지 못하는 소규모 항구까지 기항할 수 있는 것이 큰 장점입니다. 전 세계 600개 이상의 기항지를 커버하는 광범위한 노선을 자랑합니다.""",
        "features": ["세계 최고 수준 다이닝 프로그램", "르 꼬르동 블루 셰프 협업", "특식 레스토랑 무료 포함", "소형 항구 기항 가능", "전 세계 600개+ 기항지"],
        "destinations": ["지중해", "유럽", "아시아", "남미", "남태평양"],
        "cover": "https://assets.widgety.co.uk/2023/07/19/11/24/01/b17ae8a6-d8f1-4caf-9c4d-c42218a44e54/Oceania Vista - Exterior.jpg",
    },
    "Regent Seven Seas Cruises": {
        "slug": "regent-seven-seas",
        "nameKo": "리젠트 세븐 시즈 크루즈",
        "emoji": "💎",
        "tagline": "세계 최고 All-Inclusive 럭셔리 크루즈",
        "intro": """리젠트 세븐 시즈 크루즈(Regent Seven Seas Cruises)는 크루즈 업계에서 최고 수준의 럭셔리를 제공하는 울트라 럭셔리 선사입니다. 항공권(비즈니스석), 호텔 1박, 기항지 투어, 모든 음식·주류, 선내 그래티티(팁)까지 모두 포함하는 완전 All-Inclusive 시스템으로 유명합니다.

700~750명의 소규모 승객만 태우는 선박을 운영해 탁월한 1:1 서비스를 제공합니다. '세계에서 가장 럭셔리한 크루즈'라는 평가를 받으며 전 세계 상위 1% 여행자들의 선택을 받고 있습니다.""",
        "features": ["완전 All-Inclusive (항공·호텔·투어 포함)", "비즈니스 클래스 항공권 포함", "700~750명 소규모 럭셔리", "전 객실 스위트 또는 발코니", "세계 최고 럭셔리 크루즈 평가"],
        "destinations": ["지중해", "북유럽", "아시아", "남미", "극지방"],
        "cover": "https://assets.widgety.co.uk/2023/12/01/10/27/46/5e6e6e1b-1c84-462c-8a96-ed4c0fd16e89/Seven Seas Grandeur - Exterior - Regent Seven Seas Cruises.jpg",
    },
    "Disney Cruise Line": {
        "slug": "disney-cruise-line",
        "nameKo": "디즈니 크루즈 라인",
        "emoji": "🏰",
        "tagline": "온 가족이 함께하는 마법 같은 크루즈",
        "intro": """디즈니 크루즈 라인(Disney Cruise Line)은 1998년 월트 디즈니 컴퍼니가 설립한 크루즈 브랜드로, 디즈니·픽사·마블·스타워즈 캐릭터와 함께하는 세계 유일의 테마 크루즈 경험을 제공합니다. 어린이뿐 아니라 어른들도 동심으로 돌아가게 만드는 독특한 매력이 있습니다.

디즈니 캐릭터 만남 행사, 브로드웨이급 디즈니 뮤지컬 공연, 어린이 전용 클럽부터 어른 전용 나이트클럽까지 연령별 프로그램이 완벽하게 갖춰져 있습니다. 바하마에 위치한 사설 섬 캐스터웨이 케이(Castaway Cay)는 디즈니 크루즈의 시그니처 경험입니다.""",
        "features": ["디즈니·마블·스타워즈 캐릭터 경험", "브로드웨이급 디즈니 뮤지컬 공연", "사설 섬 Castaway Cay", "연령별 완벽한 프로그램", "가족 크루즈 최고 만족도"],
        "destinations": ["카리브해", "바하마", "지중해", "알래스카", "태평양"],
        "cover": "https://assets.widgety.co.uk/2022/07/27/12/46/33/14e26b22-73de-42f1-be60-c85b4a5e81c7/Disney Wish - Exterior - Disney Cruise Line.jpg",
    },
}

# ──────────────────────────────────────────
# 사이즈별 설명
# ──────────────────────────────────────────
def size_label(grt):
    if not grt: return "중형"
    if grt >= 150000: return "초대형 (메가십)"
    if grt >= 100000: return "대형"
    if grt >= 60000: return "중형"
    return "소형"

def capacity_desc(cap):
    if not cap: return ""
    if cap >= 5000: return f"최대 {cap:,}명 수용 가능한 대형 크루즈선"
    if cap >= 3000: return f"최대 {cap:,}명을 태우는 중대형 선박"
    if cap >= 1000: return f"최대 {cap:,}명의 소규모 프리미엄 선박"
    return f"최대 {cap:,}명의 럭셔리 소형 선박"

# ──────────────────────────────────────────
# HTML 공통 헤더/푸터
# ──────────────────────────────────────────
def html_head(title, desc, keywords, canonical, og_image="", depth=2):
    dots = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="keywords" content="{html.escape(keywords)}">
  <link rel="canonical" href="https://www.cruiselink.co.kr/{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="크루즈링크">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="https://www.cruiselink.co.kr/{canonical}">
  <meta property="og:image" content="{og_image}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap">
  <link rel="stylesheet" href="{dots}assets/css/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚢</text></svg>">
  {guide_css()}
</head>
<body>
<div id="header"></div>"""

def html_foot(depth=2):
    dots = "../" * depth
    return f"""
<div id="footer"></div>
<script src="{dots}assets/data/translations.js"></script>
<script src="{dots}assets/js/api.js"></script>
<script src="{dots}assets/js/components.js"></script>
<script>
  document.getElementById('header').innerHTML = Components.header('{dots}');
  document.getElementById('footer').innerHTML = Components.footer('{dots}');
</script>
</body></html>"""

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
    .g-layout{display:grid;grid-template-columns:1fr 300px;gap:36px;max-width:var(--max-width);margin:44px auto;padding:0 20px;align-items:start}
    @media(max-width:900px){.g-layout{grid-template-columns:1fr}.g-hero h1{font-size:1.5rem}}
    .g-body h2{font-size:1.3rem;font-weight:900;color:var(--navy);margin:36px 0 14px;padding-bottom:8px;border-bottom:3px solid var(--orange);display:inline-block}
    .g-body h3{font-size:1.05rem;font-weight:700;color:var(--navy);margin:20px 0 8px}
    .g-body p{color:var(--gray-700);line-height:1.9;margin-bottom:14px}
    .g-body ul{padding-left:20px;color:var(--gray-700);line-height:2;margin-bottom:14px}
    .spec-table{width:100%;border-collapse:collapse;margin:16px 0;font-size:.9rem}
    .spec-table td{padding:9px 12px;border-bottom:1px solid var(--gray-200)}
    .spec-table td:first-child{font-weight:700;color:var(--navy);width:35%;background:var(--gray-50)}
    .feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:16px 0}
    @media(max-width:600px){.feat-grid{grid-template-columns:repeat(2,1fr)}}
    .feat-card{background:var(--gray-50);border-radius:var(--radius);padding:14px;font-size:.85rem;color:var(--gray-700);border-left:3px solid var(--orange)}
    .ship-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:16px 0}
    @media(max-width:600px){.ship-grid{grid-template-columns:1fr}}
    .ship-card{border:1px solid var(--gray-200);border-radius:var(--radius);overflow:hidden;transition:box-shadow .2s;text-decoration:none;display:block;color:inherit}
    .ship-card:hover{box-shadow:var(--shadow-lg)}
    .ship-card img{width:100%;height:140px;object-fit:cover}
    .ship-card-body{padding:12px}
    .ship-card-body .name{font-weight:700;color:var(--navy);font-size:.92rem}
    .ship-card-body .meta{font-size:.78rem;color:var(--gray-500);margin-top:3px}
    .sidebar-card{background:#fff;border:1px solid var(--gray-200);border-radius:var(--radius);padding:20px;margin-bottom:18px;box-shadow:var(--shadow)}
    .sidebar-card h3{font-size:.95rem;font-weight:700;color:var(--navy);margin:0 0 14px;padding-bottom:8px;border-bottom:2px solid var(--gray-200)}
    .sidebar-toc{list-style:none;padding:0;margin:0}
    .sidebar-toc li{margin-bottom:2px}
    .sidebar-toc a{font-size:.85rem;color:var(--gray-700);text-decoration:none;padding:4px 8px;border-radius:4px;display:block;transition:all .15s}
    .sidebar-toc a:hover{background:var(--gray-100);color:var(--navy)}
    .cta-btn{display:block;background:var(--orange);color:#fff;text-align:center;padding:13px;border-radius:var(--radius);font-weight:700;font-size:.92rem;text-decoration:none;margin-top:8px;transition:background .2s}
    .cta-btn:hover{background:var(--orange-hover)}
    .cta-btn.navy{background:var(--navy)}
    .cta-btn.navy:hover{background:var(--navy-dark)}
    h2[id],h3[id]{scroll-margin-top:80px}
    .g-sidebar{position:sticky;top:80px}
    .tag{display:inline-block;background:var(--gray-100);color:var(--gray-700);font-size:.78rem;padding:3px 8px;border-radius:10px;margin:2px}
  </style>"""

# ──────────────────────────────────────────
# 선사 페이지 생성
# ──────────────────────────────────────────
def make_operator_page(op_name, op_ships):
    info = OPERATOR_INFO.get(op_name, {})
    slug = info.get("slug", re.sub(r'[^a-z0-9]+', '-', op_name.lower()).strip('-'))
    nameKo = info.get("nameKo", op_name)
    tagline = info.get("tagline", f"{op_name} 크루즈 선사 소개")
    intro = info.get("intro", f"{op_name}은(는) 세계적인 크루즈 선사입니다.")
    features = info.get("features", [])
    destinations = info.get("destinations", [])
    cover = info.get("cover", "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1200&q=80")
    emoji = info.get("emoji", "🚢")

    ship_count = len(op_ships)
    canonical = f"guide/cruise-lines/{slug}.html"
    title = f"{nameKo} 완벽 가이드 2026 | 선사 소개·선박·노선·가격 - 크루즈링크"
    desc = f"{nameKo} 선사 소개. 운항 노선, 보유 선박 {ship_count}척, 가격대, 특징 총정리. 크루즈링크 전문 상담."
    keywords = f"{nameKo}, {op_name}, 크루즈 선사, 크루즈 예약, {', '.join(destinations)}"

    # 선박 카드 HTML
    ship_cards = ""
    for s in sorted(op_ships, key=lambda x: -(x.get('grossTonnage') or 0)):
        img = s.get('coverImage','') or 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=400&q=60'
        s_slug = s.get('slug','')
        s_title = s.get('title','')
        s_titleKo = s.get('titleKo', s_title)
        grt = s.get('grossTonnage','')
        cap = s.get('capacity','')
        yr = s.get('launchYear','')
        meta_parts = []
        if yr: meta_parts.append(f"{yr}년 취항")
        if grt: meta_parts.append(f"{grt:,}톤" if isinstance(grt, int) else f"{grt}톤")
        if cap: meta_parts.append(f"정원 {cap:,}명" if isinstance(cap, int) else f"정원 {cap}명")
        meta_str = " · ".join(meta_parts)
        ship_cards += f"""
        <a class="ship-card" href="../ships/{s_slug}.html">
          <img src="{img}" alt="{html.escape(s_titleKo)}" loading="lazy"
               onerror="this.src='https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=400&q=60'">
          <div class="ship-card-body">
            <div class="name">{html.escape(s_titleKo)}</div>
            <div class="meta">{html.escape(meta_str)}</div>
          </div>
        </a>"""

    feat_html = "".join(f'<div class="feat-card">✅ {html.escape(f)}</div>' for f in features)
    dest_tags = "".join(f'<span class="tag">🌍 {html.escape(d)}</span>' for d in destinations)

    page = html_head(title, desc, keywords, canonical, cover, depth=2)
    page += f"""
<section class="g-hero">
  <img src="{cover}" alt="{html.escape(nameKo)}" loading="eager">
  <div class="g-hero-overlay"></div>
  <div class="g-hero-content">
    <div class="container">
      <div class="breadcrumb"><a href="../../">홈</a> › <a href="../">가이드</a> › <a href="./">선사 소개</a> › {html.escape(nameKo)}</div>
      <h1>{emoji} {html.escape(nameKo)}</h1>
      <div class="g-hero-meta">
        <span>🚢 {ship_count}척 보유</span>
        <span>🌍 {len(destinations)}개 주요 운항 지역</span>
      </div>
    </div>
  </div>
</section>

<div class="g-layout">
  <article class="g-body">

    <h2 id="intro">{html.escape(nameKo)} 소개</h2>
    <p><strong>{html.escape(tagline)}</strong></p>
    {"".join(f'<p>{html.escape(para.strip())}</p>' for para in intro.split(chr(10)+chr(10)) if para.strip())}

    <h2 id="features">주요 특징</h2>
    <div class="feat-grid">{feat_html}</div>

    <h2 id="destinations">운항 노선</h2>
    <p>{html.escape(nameKo)}의 주요 운항 지역은 다음과 같습니다.</p>
    <p>{dest_tags}</p>

    <h2 id="ships">보유 선박 ({ship_count}척)</h2>
    <p>아래 선박을 클릭하면 각 선박의 상세 시설 및 일정을 확인할 수 있습니다.</p>
    <div class="ship-grid">{ship_cards}</div>

    <h2 id="book">크루즈링크에서 예약하기</h2>
    <p>{html.escape(nameKo)} 예약은 크루즈링크 전문 상담원을 통해 진행할 수 있습니다. 상품 검색 후 '문의하기'를 클릭하시면 담당자가 연락드려 최적의 객실과 일정을 안내해 드립니다.</p>
    <ul>
      <li>1:1 맞춤 상담 무료 제공</li>
      <li>최신 특가·얼리버드 상품 안내</li>
      <li>객실 업그레이드 및 추가 혜택 협의 가능</li>
    </ul>

  </article>

  <aside class="g-sidebar">
    <div class="sidebar-card">
      <h3>📋 목차</h3>
      <ul class="sidebar-toc">
        <li><a href="#intro">선사 소개</a></li>
        <li><a href="#features">주요 특징</a></li>
        <li><a href="#destinations">운항 노선</a></li>
        <li><a href="#ships">보유 선박</a></li>
        <li><a href="#book">예약 안내</a></li>
      </ul>
    </div>
    <div class="sidebar-card">
      <h3>🚢 {html.escape(nameKo)} 예약 문의</h3>
      <p style="font-size:.83rem;color:var(--gray-700);margin-bottom:4px">전문 상담원이 최적 상품을 안내해 드립니다.</p>
      <a class="cta-btn" href="../../search.html">상품 검색하기</a>
      <a class="cta-btn navy" href="../../#inquiry">무료 상담 신청</a>
    </div>
  </aside>
</div>
"""
    page += html_foot(depth=2)
    return page

# ──────────────────────────────────────────
# 선박 페이지 생성
# ──────────────────────────────────────────
def make_ship_page(ship):
    slug = ship.get("slug","")
    title_en = ship.get("title","")
    title_ko = ship.get("titleKo", title_en)
    operator = ship.get("operator","")
    op_info = OPERATOR_INFO.get(operator, {})
    op_slug = op_info.get("slug", re.sub(r'[^a-z0-9]+', '-', operator.lower()).strip('-'))
    op_ko = op_info.get("nameKo", operator)

    grt = ship.get("grossTonnage") or 0
    length = ship.get("length") or 0
    width = ship.get("width") or 0
    speed = ship.get("speed") or 0
    capacity = ship.get("capacity") or 0
    crew = ship.get("crewCount") or 0
    decks = ship.get("deckCount") or 0
    cabins = ship.get("cabinCount") or 0
    launch = ship.get("launchYear","")
    ship_class = ship.get("shipClass","")
    cover = ship.get("coverImage","") or "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1200&q=80"

    detail = ships_detail.get(slug, {})
    teaser = detail.get("teaserEn","")
    intro_en = detail.get("introductionEn","")
    dining_en = detail.get("diningIntroEn","")
    entertain_en = detail.get("entertainmentIntroEn","")
    health_en = detail.get("healthIntroEn","")
    kids_en = detail.get("kidsIntroEn","")

    # 시설 목록
    facilities_html = ""
    if detail.get("entertainment"):
        items = detail["entertainment"][:6]
        cards = "".join(f'<div class="feat-card">🎭 {html.escape(it.get("title","") if isinstance(it,dict) else str(it))}</div>' for it in items)
        facilities_html += f'<h3 id="entertainment">엔터테인먼트</h3><div class="feat-grid">{cards}</div>'
    if detail.get("dining"):
        items = detail["dining"][:6]
        cards = "".join(f'<div class="feat-card">🍽️ {html.escape(it.get("title","") if isinstance(it,dict) else str(it))}</div>' for it in items)
        facilities_html += f'<h3 id="dining">레스토랑 & 바</h3><div class="feat-grid">{cards}</div>'
    if detail.get("health"):
        items = detail["health"][:6]
        cards = "".join(f'<div class="feat-card">💆 {html.escape(it.get("title","") if isinstance(it,dict) else str(it))}</div>' for it in items)
        facilities_html += f'<h3 id="spa">스파 & 웰니스</h3><div class="feat-grid">{cards}</div>'
    if detail.get("kids"):
        items = detail["kids"][:4]
        cards = "".join(f'<div class="feat-card">🧒 {html.escape(it.get("title","") if isinstance(it,dict) else str(it))}</div>' for it in items)
        facilities_html += f'<h3 id="kids">키즈 프로그램</h3><div class="feat-grid">{cards}</div>'

    # 관련 크루즈 JS
    cruise_js = f"""
  (async()=>{{
    try{{
      const all = await API.loadAllCruises();
      const today = new Date().toISOString().slice(0,10);
      const list = all.filter(c=>c.shipSlug==='{slug}'&&c.dateFrom>=today).slice(0,4);
      const el = document.getElementById('related-list');
      if(!list.length){{el.innerHTML='<p style="font-size:.83rem;color:var(--gray-500)">현재 출발 예정 상품이 없습니다</p>';return;}}
      el.innerHTML=list.map(c=>`<a style="display:flex;gap:10px;padding:10px 0;border-bottom:1px solid var(--gray-200);text-decoration:none;color:inherit" href="../../cruise-view.html?ref=${{c.ref}}&ship=${{c.shipSlug}}"><img src="${{c.image}}" style="width:68px;height:50px;object-fit:cover;border-radius:4px;flex-shrink:0" onerror="this.src='https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=120&q=60'"><div><div style="font-size:.83rem;font-weight:700;color:var(--navy)">${{c.title}}</div><div style="font-size:.76rem;color:var(--gray-500)">${{c.dateFrom}} · ${{c.nights}}박</div><div style="font-size:.86rem;font-weight:700;color:var(--orange)">$${{c.priceInside||c.priceOutside||'?'}}~</div></div></a>`).join('');
    }}catch(e){{}}
  }})();"""

    # 스펙 행 생성
    spec_rows = ""
    if launch: spec_rows += f"<tr><td>취항 연도</td><td>{launch}년</td></tr>"
    if ship_class: spec_rows += f"<tr><td>선박 클래스</td><td>{html.escape(ship_class)}</td></tr>"
    if grt: spec_rows += f"<tr><td>총톤수 (GRT)</td><td>{grt:,}톤</td></tr>"
    if length: spec_rows += f"<tr><td>전체 길이</td><td>{length}m</td></tr>"
    if width: spec_rows += f"<tr><td>전체 폭</td><td>{width}m</td></tr>"
    if speed: spec_rows += f"<tr><td>최고 속도</td><td>{speed}노트</td></tr>"
    if decks: spec_rows += f"<tr><td>갑판 수</td><td>{decks}개 갑판</td></tr>"
    if cabins: spec_rows += f"<tr><td>객실 수</td><td>{cabins:,}실</td></tr>"
    if capacity: spec_rows += f"<tr><td>최대 승객 수</td><td>{capacity:,}명</td></tr>"
    if crew: spec_rows += f"<tr><td>승무원 수</td><td>{crew:,}명</td></tr>"
    spec_rows += f"<tr><td>운항 선사</td><td>{html.escape(op_ko)}</td></tr>"

    canonical = f"guide/ships/{slug}.html"
    pg_title = f"{html.escape(title_ko)} 완벽 가이드 2026 | 시설·객실·일정 총정리 - 크루즈링크"
    desc = f"{html.escape(title_ko)} ({html.escape(title_en)}) 선내 시설, 객실, 레스토랑, 2026 운항 일정 및 가격 총정리. {html.escape(op_ko)} 전문 예약."
    keywords = f"{html.escape(title_ko)}, {html.escape(title_en)}, {html.escape(op_ko)}, 크루즈 예약, 크루즈 시설"

    # 소개 텍스트 (영문 없으면 기본 생성)
    if intro_en and len(intro_en) > 100:
        # 영문 소개를 적절히 구조화 (실제 번역 없이 요약 활용)
        intro_p = f"<p>{html.escape(title_ko)}은(는) {html.escape(op_ko)}의 {size_label(grt)} 크루즈선으로, {launch+'년 취항한 ' if launch else ''}{capacity_desc(capacity) if capacity else ''}입니다. 다양한 시설과 엔터테인먼트를 갖추고 전 세계 주요 항구를 기항합니다.</p>"
    else:
        intro_p = f"<p>{html.escape(title_ko)}은(는) {html.escape(op_ko)}가 운항하는 {size_label(grt)} 크루즈선입니다. {capacity_desc(capacity) if capacity else ''} 최첨단 시설과 다양한 엔터테인먼트, 레스토랑을 갖추고 전 세계 주요 크루즈 목적지를 운항합니다.</p>"

    page = html_head(pg_title, desc, keywords, canonical, cover, depth=2)
    page += f"""
<section class="g-hero">
  <img src="{cover}" alt="{html.escape(title_ko)}" loading="eager">
  <div class="g-hero-overlay"></div>
  <div class="g-hero-content">
    <div class="container">
      <div class="breadcrumb"><a href="../../">홈</a> › <a href="../">가이드</a> › <a href="./">선박 소개</a> › {html.escape(title_ko)}</div>
      <h1>🚢 {html.escape(title_ko)} 완벽 가이드 2026</h1>
      <div class="g-hero-meta">
        <span>🏢 {html.escape(op_ko)}</span>
        {f'<span>📅 {launch}년 취항</span>' if launch else ''}
        {f'<span>👥 최대 {capacity:,}명</span>' if capacity else ''}
        {f'<span>⚓ {grt:,} GRT</span>' if grt else ''}
      </div>
    </div>
  </div>
</section>

<div class="g-layout">
  <article class="g-body">

    <h2 id="intro">{html.escape(title_ko)} 소개</h2>
    {intro_p}
    <p>크루즈링크에서는 {html.escape(op_ko)}의 {html.escape(title_ko)} 탑승 상품을 전문 상담을 통해 예약할 수 있습니다. 아시아·지중해·알래스카 등 다양한 노선에서 {html.escape(title_ko)}를 만나보세요.</p>

    <h2 id="specs">선박 제원</h2>
    <table class="spec-table"><tbody>{spec_rows}</tbody></table>

    {"<h2 id='facilities'>선내 주요 시설</h2>" + facilities_html if facilities_html else ""}

    <h2 id="book">예약 안내</h2>
    <p>{html.escape(title_ko)} 탑승 크루즈 상품은 크루즈링크를 통해 예약하실 수 있습니다.</p>
    <ul>
      <li>아래 '상품 보기'에서 출발일별 가격을 확인하세요</li>
      <li>'무료 상담 신청'으로 전문 상담원의 맞춤 안내를 받으세요</li>
      <li>특가·얼리버드 상품은 빠르게 소진되므로 미리 문의하시길 권장합니다</li>
    </ul>

  </article>

  <aside class="g-sidebar">
    <div class="sidebar-card">
      <h3>📋 목차</h3>
      <ul class="sidebar-toc">
        <li><a href="#intro">선박 소개</a></li>
        <li><a href="#specs">선박 제원</a></li>
        {"<li><a href='#facilities'>선내 시설</a></li>" if facilities_html else ""}
        <li><a href="#book">예약 안내</a></li>
      </ul>
    </div>
    <div class="sidebar-card">
      <h3>🔥 출발 예정 상품</h3>
      <div id="related-list"><p style="font-size:.83rem;color:var(--gray-500)">로딩 중...</p></div>
    </div>
    <div class="sidebar-card">
      <h3>🚢 예약 문의</h3>
      <a class="cta-btn" href="../../search.html?ship={slug}">상품 보기</a>
      <a class="cta-btn navy" href="../../#inquiry">무료 상담 신청</a>
    </div>
    <div class="sidebar-card">
      <h3>🏢 선사 정보</h3>
      <p style="font-size:.83rem;color:var(--gray-700);margin-bottom:8px">{html.escape(op_ko)} 더 알아보기</p>
      <a class="cta-btn navy" href="../cruise-lines/{op_slug}.html">{html.escape(op_ko)} 소개 보기</a>
    </div>
  </aside>
</div>
"""
    page += f"""
<script>
  document.getElementById('header').innerHTML = Components.header('../../');
  document.getElementById('footer').innerHTML = Components.footer('../../');
  {cruise_js}
</script>
</body></html>"""
    # html_foot 대신 직접 삽입 (script 합침)
    return page

# ──────────────────────────────────────────
# Guide 인덱스 페이지
# ──────────────────────────────────────────
def make_guide_index():
    op_cards = ""
    for op_name, op_ships in sorted(by_operator.items(), key=lambda x: -len(x[1])):
        info = OPERATOR_INFO.get(op_name, {})
        slug = info.get("slug", re.sub(r'[^a-z0-9]+', '-', op_name.lower()).strip('-'))
        nameKo = info.get("nameKo", op_name)
        emoji = info.get("emoji","🚢")
        tagline = info.get("tagline","")
        op_cards += f"""
        <a class="ship-card" href="cruise-lines/{slug}.html">
          <div style="padding:20px;background:var(--navy);color:#fff;text-align:center">
            <div style="font-size:2rem">{emoji}</div>
            <div style="font-weight:900;font-size:1rem;margin-top:8px">{html.escape(nameKo)}</div>
            <div style="font-size:.78rem;opacity:.8;margin-top:4px">{len(op_ships)}척 보유</div>
          </div>
          <div class="ship-card-body">
            <div class="name" style="font-size:.82rem;font-weight:400;color:var(--gray-700)">{html.escape(tagline)}</div>
          </div>
        </a>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>크루즈 완벽 가이드 | 선사·선박·기항지 정보 총정리 - 크루즈링크</title>
  <meta name="description" content="MSC, NCL, 로열 캐리비안 등 주요 크루즈 선사 소개, 선박별 시설 가이드, 기항지 정보까지 크루즈링크가 총정리합니다.">
  <link rel="canonical" href="https://www.cruiselink.co.kr/guide/">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap">
  <link rel="stylesheet" href="../assets/css/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚢</text></svg>">
  {guide_css()}
</head>
<body>
<div id="header"></div>

<section style="background:linear-gradient(135deg,var(--navy) 0%,#283593 100%);color:#fff;padding:80px 0;text-align:center">
  <div class="container">
    <h1 style="font-size:2.2rem;font-weight:900;margin:0 0 12px">크루즈 완벽 가이드</h1>
    <p style="font-size:1.05rem;opacity:.85;margin:0">선사·선박·기항지 정보를 한곳에서 확인하세요</p>
  </div>
</section>

<div class="container" style="padding:48px 20px">

  <section style="margin-bottom:56px">
    <h2 style="font-size:1.4rem;font-weight:900;color:var(--navy);margin-bottom:8px">🏢 선사 소개</h2>
    <p style="color:var(--gray-700);margin-bottom:24px">세계 주요 크루즈 선사들의 특징과 노선, 보유 선박을 소개합니다.</p>
    <div class="ship-grid">{op_cards}</div>
  </section>

  <section style="margin-bottom:56px">
    <h2 style="font-size:1.4rem;font-weight:900;color:var(--navy);margin-bottom:8px">🚢 선박 소개</h2>
    <p style="color:var(--gray-700);margin-bottom:24px">각 선박의 시설, 객실, 운항 노선을 상세히 안내합니다. <a href="ships/" style="color:var(--orange);font-weight:700">전체 보기 →</a></p>
  </section>

  <section style="margin-bottom:56px">
    <h2 style="font-size:1.4rem;font-weight:900;color:var(--navy);margin-bottom:8px">🌍 기항지 가이드</h2>
    <p style="color:var(--gray-700);margin-bottom:24px">크루즈 기항지별 볼거리, 맛집, 투어 정보를 정리합니다. <a href="ports/" style="color:var(--orange);font-weight:700">전체 보기 →</a></p>
  </section>

</div>

<div id="footer"></div>
<script src="../assets/data/translations.js"></script>
<script src="../assets/js/api.js"></script>
<script src="../assets/js/components.js"></script>
<script>
  document.getElementById('header').innerHTML = Components.header('../');
  document.getElementById('footer').innerHTML = Components.footer('../');
</script>
</body></html>"""

# ──────────────────────────────────────────
# 생성 실행
# ──────────────────────────────────────────
print("=== CruiseLink Guide Generator ===")

# 1) 가이드 인덱스
with open(OUT / "index.html", "w", encoding="utf-8") as f:
    f.write(make_guide_index())
print("✅ guide/index.html")

# 2) 선사 페이지 (cruise-lines/)
for op_name, op_ships in by_operator.items():
    info = OPERATOR_INFO.get(op_name, {})
    slug = info.get("slug", re.sub(r'[^a-z0-9]+', '-', op_name.lower()).strip('-'))
    page = make_operator_page(op_name, op_ships)
    path = OUT / "cruise-lines" / f"{slug}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"  ✅ cruise-lines/{slug}.html ({len(op_ships)}척)")

print(f"\n총 선사 페이지: {len(by_operator)}개")

# 3) 선박 페이지 (ships/) — MSC Bellissima는 이미 수동 제작, 덮어씀
skip_slugs = set()  # 건너뛸 slug 없음 (수동 제작 버전은 덮어쓰지 않음)
count = 0
for ship in ships:
    slug = ship.get("slug","")
    if slug == "msc-bellissima":
        print(f"  ⏭️  ships/msc-bellissima.html (수동 제작 버전 유지)")
        continue
    page = make_ship_page(ship)
    path = OUT / "ships" / f"{slug}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    count += 1

print(f"\n총 선박 페이지: {count}개 (+ msc-bellissima 수동 유지)")
print(f"\n🎉 총 생성: {1 + len(by_operator) + count}개 페이지")
print("완료!")
