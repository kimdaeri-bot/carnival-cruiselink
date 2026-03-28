#!/usr/bin/env python3
"""
크루즈 일정 소개 페이지 자동 생성 (하루 20개)
- 크루즈 데이터 assets/data/cruises*.json 에서 읽기
- /guide/cruises/[ref]/ 에 SEO 최적화 페이지 생성
- blog-draft 2개 동시 생성 (기존 루틴 유지)
- sitemap 자동 업데이트
"""
import json, os, re, glob, random
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, 'assets/data')
OUT_DIR = os.path.join(BASE, 'guide/cruises')
SITEMAP = os.path.join(BASE, 'sitemap.xml')
CRUISES_INDEX = os.path.join(OUT_DIR, 'index.html')
os.makedirs(OUT_DIR, exist_ok=True)

TODAY = datetime.now().strftime('%Y-%m-%d')
DAILY_LIMIT = 200

def load_cruises():
    """모든 cruises json 파일에서 크루즈 데이터 로드"""
    cruises = []
    for f in sorted(glob.glob(os.path.join(DATA_DIR, 'cruises*.json'))):
        try:
            with open(f) as fp:
                data = json.load(fp)
                if isinstance(data, list):
                    cruises.extend(data)
                elif isinstance(data, dict) and 'cruises' in data:
                    cruises.extend(data['cruises'])
        except Exception as e:
            print(f"  SKIP {f}: {e}")
    return cruises

def slug_from_ref(ref, cruise):
    """크루즈 ref → URL slug"""
    ref_clean = re.sub(r'[^a-zA-Z0-9-]', '-', str(ref)).lower().strip('-')
    return ref_clean[:60]

def already_exists(slug):
    return os.path.exists(os.path.join(OUT_DIR, slug, 'index.html'))

def format_price(price, currency='USD'):
    if not price:
        return '문의'
    try:
        p = int(float(price))
        sym = '$' if currency == 'USD' else (currency + ' ')
        return f"{sym}{p:,}"
    except:
        return str(price)

def make_port_route(cruise):
    route = cruise.get('portRoute') or cruise.get('port_route') or ''
    if route:
        return route
    ports = cruise.get('ports', [])
    if ports:
        names = [p.get('nameKo') or p.get('name', '') for p in ports[:6]]
        return ' → '.join(filter(None, names))
    return ''

def make_itinerary_html(cruise):
    """일정 테이블 생성"""
    itinerary = cruise.get('itinerary') or cruise.get('days') or []
    if not itinerary:
        return ''
    
    rows = ''
    for i, day in enumerate(itinerary[:10], 1):
        if isinstance(day, dict):
            port = day.get('nameKo') or day.get('name') or day.get('port', '')
            arrival = day.get('arrival', '') or day.get('arrivalTime', '')
            departure = day.get('departure', '') or day.get('departureTime', '')
        else:
            port = str(day)
            arrival = departure = ''
        rows += f'<tr><td>Day {i}</td><td>{port}</td><td>{arrival or "-"}</td><td>{departure or "-"}</td></tr>'
    
    if not rows:
        return ''
    
    return f'''<table>
<thead><tr><th>일차</th><th>기항지</th><th>입항</th><th>출항</th></tr></thead>
<tbody>{rows}</tbody>
</table>'''

def build_cruise_page(cruise):
    ref = cruise.get('ref') or cruise.get('id') or ''
    slug = slug_from_ref(ref, cruise)
    if not slug or already_exists(slug):
        return None, None
    
    # 기본 정보
    title_ko = cruise.get('title') or cruise.get('titleKo') or ''
    ship_title = cruise.get('shipTitle') or cruise.get('shipTitleKo') or ''
    operator = cruise.get('operator') or cruise.get('operatorTitle') or ''
    nights = cruise.get('nights') or ''
    date_from = cruise.get('dateFrom') or cruise.get('date_from') or ''
    date_to = cruise.get('dateTo') or cruise.get('date_to') or ''
    port_route = make_port_route(cruise)
    image = cruise.get('image') or ''
    price_inside = cruise.get('priceInside') or cruise.get('price_inside') or ''
    price_balcony = cruise.get('priceBalcony') or cruise.get('price_balcony') or ''
    currency = cruise.get('currency') or 'USD'
    
    if not title_ko and ship_title:
        title_ko = f"{ship_title} {nights}박 크루즈"
    if not title_ko:
        return None, None
    
    # 날짜 포맷
    dep_str = ''
    if date_from:
        try:
            from datetime import datetime as dt
            d = dt.strptime(date_from[:10], '%Y-%m-%d')
            dep_str = d.strftime('%Y년 %m월 %d일')
        except:
            dep_str = date_from[:10]
    
    itinerary_html = make_itinerary_html(cruise)
    route_display = port_route[:100] if port_route else ''
    
    price_html = ''
    if price_inside or price_balcony:
        price_html = f'''<div class="cruise-section">
<h2>💰 요금 안내</h2>
<table>
<thead><tr><th>객실 등급</th><th>1인 요금 (2인 기준)</th></tr></thead>
<tbody>
{"<tr><td>내부 객실</td><td class='price'>" + format_price(price_inside, currency) + "~</td></tr>" if price_inside else ""}
{"<tr><td>발코니 객실</td><td class='price'>" + format_price(price_balcony, currency) + "~</td></tr>" if price_balcony else ""}
</tbody>
</table>
<p style="font-size:.82rem;color:#9e9e9e">※ 2인 1실 기준. 세금·항만료·팁 별도.</p>
</div>'''
    
    itinerary_section = ''
    if itinerary_html:
        itinerary_section = f'''<div class="cruise-section">
<h2>🗺️ 상세 일정</h2>
{itinerary_html}
</div>'''
    elif route_display:
        itinerary_section = f'''<div class="cruise-section">
<h2>🗺️ 항로</h2>
<div class="route-box"><p>{route_display}</p></div>
</div>'''
    
    desc = f"{title_ko[:80]} — {nights}박 크루즈 일정, 기항지, 가격 총정리."
    hero_html = f'<img class="cruise-hero-img" src="{image}" alt="{title_ko}" loading="eager">' if image else ''
    clean_title = re.sub(r'[\U0001F300-\U0001FFFF]', '', title_ko).strip()
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-K4PPLZNG');</script>
<!-- End Google Tag Manager -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{clean_title} | 크루즈링크</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="https://www.cruiselink.co.kr/guide/cruises/{slug}/">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="크루즈링크">
  <meta property="og:title" content="{clean_title} | 크루즈링크">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="https://www.cruiselink.co.kr/guide/cruises/{slug}/">
  <meta property="og:image" content="{image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{image}">
  <!-- JSON-LD: Article -->
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Article","headline":"{clean_title}","description":"{desc}","image":"{image}","author":{{"@type":"Organization","name":"크루즈링크"}},"publisher":{{"@type":"Organization","name":"크루즈링크","url":"https://www.cruiselink.co.kr"}},"datePublished":"{TODAY}"}}
  </script>
  <!-- JSON-LD: BreadcrumbList -->
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
    {{"@type":"ListItem","position":1,"name":"홈","item":"https://www.cruiselink.co.kr/"}},
    {{"@type":"ListItem","position":2,"name":"크루즈 가이드","item":"https://www.cruiselink.co.kr/guide/"}},
    {{"@type":"ListItem","position":3,"name":"크루즈 일정 소개","item":"https://www.cruiselink.co.kr/guide/cruises/"}},
    {{"@type":"ListItem","position":4,"name":"{clean_title}","item":"https://www.cruiselink.co.kr/guide/cruises/{slug}/"}}
  ]}}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap">
  <link rel="stylesheet" href="../../../assets/css/style.css">
  <link rel="icon" type="image/png" href="../../../assets/images/favicon.png">
  <link rel="shortcut icon" href="../../../favicon.ico">
  <style>
    .cruise-hero-img{{width:100%;max-height:460px;object-fit:cover;display:block}}
    .cruise-wrap{{padding:28px 20px 80px}}
    .cruise-title{{font-size:1.6rem;font-weight:900;color:#1a237e;line-height:1.4;margin-bottom:8px}}
    .cruise-meta{{font-size:.83rem;color:#9e9e9e;margin-bottom:28px;display:flex;gap:8px;flex-wrap:wrap}}
    .cruise-meta span{{background:#f0f4ff;color:#1a237e;padding:3px 10px;border-radius:10px;font-weight:600}}
    .cruise-section{{margin-bottom:28px;padding-bottom:28px;border-bottom:1px solid #f0f0f0}}
    .cruise-section h2{{font-size:1.1rem;font-weight:900;color:#1a237e;margin:0 0 12px;padding-bottom:8px;border-bottom:2px solid #ff6f00;display:inline-block}}
    .cruise-section p,.cruise-section li{{color:#616161;line-height:1.9;font-size:.97rem}}
    .cruise-section ul{{padding-left:20px;margin-bottom:10px}}
    .cruise-section table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem}}
    .cruise-section th{{background:#1a237e;color:#fff;padding:9px 12px;text-align:left}}
    .cruise-section td{{padding:9px 12px;border-bottom:1px solid #e8eaed}}
    .cruise-section td.price{{color:#e65100;font-weight:800}}
    .route-box{{background:#f0f7ff;border-radius:8px;padding:16px 20px}}
    .cta-box{{background:linear-gradient(135deg,#1a237e,#0d47a1);color:#fff;padding:28px;text-align:center;border-radius:12px;margin:28px 0}}
    .cta-box h3{{color:#ffd700;font-size:1.05rem;margin-bottom:8px}}
    .cta-btns{{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:14px}}
    .cta-btns a{{color:#fff;background:rgba(255,255,255,.18);padding:9px 20px;border-radius:20px;font-size:.85rem;font-weight:700;text-decoration:none}}
    .cta-btns a:hover{{background:rgba(255,255,255,.3)}}
    @media(max-width:768px){{
      *{{-webkit-box-sizing:border-box;box-sizing:border-box}}
      html,body{{overflow-x:hidden;width:100%}}
      .cruise-hero-img{{max-height:260px}}
      .cruise-wrap{{padding:24px 16px 60px}}
      .cruise-title{{font-size:1.2rem}}
      .cruise-meta{{gap:6px}}
      .cruise-section h2{{font-size:1rem}}
      .cruise-section p,.cruise-section li{{font-size:.93rem;line-height:1.8}}
      .table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:12px 0}}
      .cruise-section table{{min-width:420px}}
      .cta-box{{padding:20px 16px}}
      .cta-btns{{flex-direction:column;gap:8px}}
      .cta-btns a{{width:100%;text-align:center;padding:12px}}
      .route-box{{padding:12px 14px}}
      .tip-box{{padding:12px 14px;font-size:.88rem}}
    }}
  </style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-K4PPLZNG" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<div id="header"></div>

{hero_html}

<div class="cruise-wrap">
  <div style="font-size:.82rem;color:#9e9e9e;margin-bottom:12px">
    <a href="/" style="color:#9e9e9e;text-decoration:none">홈</a> › 
    <a href="/guide/" style="color:#9e9e9e;text-decoration:none">가이드</a> › 
    <a href="/guide/cruises/" style="color:#9e9e9e;text-decoration:none">크루즈 일정 소개</a> › 
    {clean_title[:30]}
  </div>

  <h1 class="cruise-title">{title_ko}</h1>
  <div class="cruise-meta">
    {"<span>🌙 " + str(nights) + "박 " + str(int(nights)+1) + "일</span>" if nights else ""}
    {"<span>📅 " + dep_str + " 출발</span>" if dep_str else ""}
    {"<span>🚢 " + ship_title + "</span>" if ship_title else ""}
    {"<span>" + operator + "</span>" if operator else ""}
  </div>

  <div class="cruise-section">
    <h2>🚢 크루즈 소개</h2>
    <p>{title_ko}은(는) 크루즈링크에서 예약 가능한 인기 상품입니다. {"출발일: " + dep_str if dep_str else ""} {"· " + str(nights) + "박 " + str(int(nights)+1) + "일" if nights else ""} {"· " + route_display if route_display else ""}</p>
  </div>

  {itinerary_section}
  {price_html}

  <div class="cta-box">
    <h3>🚢 지금 바로 예약 문의하세요</h3>
    <p>전문 상담원이 최적의 객실과 특가를 안내해 드립니다.</p>
    <div class="cta-btns">
      <a href="/cruise-view/?ref={ref}">상세 상품 보기</a>
      <a href="/search/">크루즈 검색</a>
      <a href="https://pf.kakao.com/_xgYbJG" target="_blank">카카오톡 상담</a>
      <a href="tel:02-3788-9119">☎ 02-3788-9119</a>
    </div>
  </div>
</div>

<div id="footer"></div>
<script src="../../../assets/data/translations.js"></script>
<script src="../../../assets/js/api.js"></script>
<script src="../../../assets/js/components.js"></script>
<script>
  document.getElementById('header').innerHTML = Components.header('guide', '../../../');
  document.getElementById('footer').innerHTML = Components.footer('../../../');
</script>
</body></html>'''
    
    return slug, html

def add_to_sitemap(slugs):
    with open(SITEMAP) as f:
        content = f.read()
    
    new_urls = ''
    for slug in slugs:
        url = f'https://www.cruiselink.co.kr/guide/cruises/{slug}/'
        if url not in content:
            new_urls += f'  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n'
    
    if new_urls:
        content = content.replace(
            '  <url><loc>https://www.cruiselink.co.kr/guide/faq/</loc>',
            new_urls + '  <url><loc>https://www.cruiselink.co.kr/guide/faq/</loc>'
        )
        with open(SITEMAP, 'w') as f:
            f.write(content)

def main():
    print(f"[{TODAY}] 크루즈 일정 소개 페이지 자동 생성 시작")
    
    cruises = load_cruises()
    print(f"총 {len(cruises)}개 크루즈 데이터 로드")
    
    # 이미 생성된 것 제외
    existing = set(os.listdir(OUT_DIR))
    todo = [c for c in cruises if slug_from_ref(c.get('ref',''), c) not in existing]
    
    # 오늘 생성할 20개 선택 (가격 있는 것 우선)
    todo_with_price = [c for c in todo if c.get('priceInside') or c.get('priceBalcony')]
    todo_no_price = [c for c in todo if not (c.get('priceInside') or c.get('priceBalcony'))]
    
    selected = (todo_with_price + todo_no_price)[:DAILY_LIMIT]
    
    created_slugs = []
    for cruise in selected:
        slug, html = build_cruise_page(cruise)
        if not slug:
            continue
        out_path = os.path.join(OUT_DIR, slug, 'index.html')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w') as f:
            f.write(html)
        created_slugs.append(slug)
        print(f"  ✅ {slug}")
    
    if created_slugs:
        add_to_sitemap(created_slugs)
        rebuild_index()
        print(f"\n✅ {len(created_slugs)}개 생성 완료 → sitemap + 인덱스 업데이트")
    else:
        print("새로 생성할 페이지 없음 (모두 기존)")

def rebuild_index():
    """guide/cruises/index.html 전체 재생성"""
    import re as _re
    items = []
    for d in sorted(os.listdir(OUT_DIR)):
        if d == 'index.html':
            continue
        p = os.path.join(OUT_DIR, d, 'index.html')
        if not os.path.exists(p):
            continue
        with open(p) as f:
            html = f.read()
        title_m = _re.search(r'<title>([^<]+)</title>', html)
        title = title_m.group(1).replace(' | 크루즈링크', '').strip() if title_m else d
        og_img_m = _re.search(r'property="og:image" content="([^"]+)"', html)
        img = og_img_m.group(1) if og_img_m else ''
        nights_m = _re.search(r'🌙 (\d+)박', html)
        nights = nights_m.group(1) if nights_m else ''
        items.append({'slug': d, 'title': title, 'img': img, 'nights': nights})

    cards = ''
    for it in items:
        hero = it['img'] or 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=70'
        nights_str = f"🌙 {it['nights']}박" if it['nights'] else '🚢 크루즈'
        cards += f'''
    <a class="cruise-idx-card" href="{it['slug']}/" data-slug="{it['slug']}">
      <div class="cruise-idx-img-wrap">
        <img src="{hero}" alt="{it['title']}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=70'">
      </div>
      <div class="cruise-idx-body">
        <div class="cruise-idx-badge">{nights_str}</div>
        <h2>{it['title'][:60]}</h2>
        <span class="cruise-idx-btn">자세히 보기 →</span>
      </div>
    </a>'''

    total = len(items)
    index_html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-K4PPLZNG');</script>
<!-- End Google Tag Manager -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>크루즈 일정 소개 — 노선별 상세 가이드 | 크루즈링크</title>
  <meta name="description" content="지중해·알래스카·카리브해·동아시아 등 크루즈 노선별 상세 일정 소개. MSC·NCL·로열캐리비안·카니발·셀레브리티 실제 상품 기반 완벽 가이드.">
  <link rel="canonical" href="https://www.cruiselink.co.kr/guide/cruises/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="크루즈링크">
  <meta property="og:title" content="크루즈 일정 소개 — 노선별 상세 가이드 | 크루즈링크">
  <meta property="og:description" content="지중해·알래스카·카리브해·동아시아 크루즈 노선별 상세 일정 소개.">
  <meta property="og:url" content="https://www.cruiselink.co.kr/guide/cruises/">
  <meta property="og:image" content="https://www.cruiselink.co.kr/assets/images/cta-web.png">
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
    {{"@type":"ListItem","position":1,"name":"홈","item":"https://www.cruiselink.co.kr/"}},
    {{"@type":"ListItem","position":2,"name":"크루즈 가이드","item":"https://www.cruiselink.co.kr/guide/"}},
    {{"@type":"ListItem","position":3,"name":"크루즈 일정 소개","item":"https://www.cruiselink.co.kr/guide/cruises/"}}
  ]}}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap">
  <link rel="stylesheet" href="../../assets/css/style.css">
  <link rel="icon" type="image/png" href="../../assets/images/favicon.png">
  <link rel="shortcut icon" href="../../favicon.ico">
  <style>
    .cruises-hero{{background:linear-gradient(135deg,#0a2540,#1565c0);color:#fff;padding:48px 0 36px;text-align:center}}
    .cruises-hero h1{{font-size:1.9rem;font-weight:900;margin-bottom:10px}}
    .cruises-hero p{{opacity:.85;font-size:.97rem;max-width:600px;margin:0 auto}}
    .cruises-wrap{{padding:32px 20px 80px}}
    .filter-tabs{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:24px}}
    .filter-tab{{padding:7px 16px;border:1.5px solid #e0e4ee;border-radius:20px;background:#fff;cursor:pointer;font-size:.83rem;font-weight:600;color:#555;transition:all .15s}}
    .filter-tab.active,.filter-tab:hover{{background:#1a237e;color:#fff;border-color:#1a237e}}
    .result-count{{font-size:.85rem;color:#9e9e9e;margin-bottom:16px}}
    .cruise-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}}
    .cruise-idx-card{{background:#fff;border:1px solid #e8eaed;border-radius:12px;overflow:hidden;text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:box-shadow .2s,transform .2s}}
    .cruise-idx-card:hover{{box-shadow:0 6px 20px rgba(0,0,0,.1);transform:translateY(-2px)}}
    .cruise-idx-img-wrap{{height:160px;overflow:hidden}}
    .cruise-idx-img-wrap img{{width:100%;height:100%;object-fit:cover;transition:transform .3s}}
    .cruise-idx-card:hover .cruise-idx-img-wrap img{{transform:scale(1.05)}}
    .cruise-idx-body{{padding:14px 16px 16px;flex:1;display:flex;flex-direction:column}}
    .cruise-idx-badge{{background:#e8f0fe;color:#1a237e;font-size:.73rem;font-weight:700;padding:2px 8px;border-radius:8px;display:inline-block;margin-bottom:6px}}
    .cruise-idx-body h2{{font-size:.88rem;font-weight:700;color:#1a237e;line-height:1.5;margin-bottom:auto;padding-bottom:10px}}
    .cruise-idx-btn{{display:inline-block;background:#ff6f00;color:#fff;padding:6px 14px;border-radius:7px;font-size:.78rem;font-weight:700;margin-top:10px;transition:background .2s}}
    .cruise-idx-card:hover .cruise-idx-btn{{background:#e65100}}
    @media(max-width:600px){{.cruise-grid{{grid-template-columns:1fr 1fr;gap:10px}}.cruise-idx-img-wrap{{height:120px}}}}
  </style>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-K4PPLZNG" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<div id="header"></div>
<section class="cruises-hero">
  <div class="container">
    <div style="font-size:.8rem;opacity:.7;margin-bottom:10px">
      <a href="/" style="color:rgba(255,255,255,.75);text-decoration:none">홈</a> › 
      <a href="/guide/" style="color:rgba(255,255,255,.75);text-decoration:none">크루즈 가이드</a> › 
      크루즈 일정 소개
    </div>
    <h1>🚢 크루즈 일정 소개</h1>
    <p>실제 출발 크루즈 상품의 상세 일정, 기항지, 선박 정보를 한눈에 확인하세요.</p>
  </div>
</section>
<div class="cruises-wrap">
  <div class="filter-tabs">
    <button class="filter-tab active" onclick="filterCards('all',this)">전체 ({total})</button>
    <button class="filter-tab" onclick="filterCards('msc',this)">MSC</button>
    <button class="filter-tab" onclick="filterCards('ncl',this)">NCL</button>
    <button class="filter-tab" onclick="filterCards('celebrity',this)">셀레브리티</button>
    <button class="filter-tab" onclick="filterCards('carnival',this)">카니발</button>
    <button class="filter-tab" onclick="filterCards('rci',this)">로열캐리비안</button>
    <button class="filter-tab" onclick="filterCards('oceania',this)">오세아니아</button>
    <button class="filter-tab" onclick="filterCards('alaska',this)">알래스카</button>
    <button class="filter-tab" onclick="filterCards('mediterranean',this)">지중해</button>
    <button class="filter-tab" onclick="filterCards('caribbean',this)">카리브해</button>
    <button class="filter-tab" onclick="filterCards('korea',this)">동아시아</button>
  </div>
  <div class="result-count" id="resultCount">총 {total}개</div>
  <div class="cruise-grid" id="cruiseGrid">{cards}
  </div>
</div>
<div id="footer"></div>
<script src="../../assets/data/translations.js"></script>
<script src="../../assets/js/api.js"></script>
<script src="../../assets/js/components.js"></script>
<script>
  document.getElementById('header').innerHTML = Components.header('guide', '../../');
  document.getElementById('footer').innerHTML = Components.footer('../../');
  function filterCards(keyword, btn) {{
    document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    let visible = 0;
    document.querySelectorAll('.cruise-idx-card').forEach(card => {{
      if (keyword === 'all') {{ card.style.display = ''; visible++; }}
      else {{
        const slug = card.dataset.slug || '';
        const title = card.querySelector('h2')?.textContent.toLowerCase() || '';
        const match = slug.includes(keyword) || title.includes(keyword);
        card.style.display = match ? '' : 'none';
        if (match) visible++;
      }}
    }});
    document.getElementById('resultCount').textContent = '총 ' + visible + '개';
  }}
</script>
</body></html>'''

    with open(os.path.join(OUT_DIR, 'index.html'), 'w') as f:
        f.write(index_html)
    print(f"  📋 index.html 재생성 완료 ({total}개)")

if __name__ == '__main__':
    main()
