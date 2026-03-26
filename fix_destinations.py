#!/usr/bin/env python3
"""
1. 'other' destination 재분류 (portRoute/countries 기반)
2. Princess Cruises Widgety API 재수집
"""
import json, time, urllib.request, re
from collections import Counter

BASE = "/Users/kim/.openclaw/workspace/cruiselink-v2"
CRUISES_FILE = f"{BASE}/assets/data/cruises.json"
API_AUTH = "app_id=fdb0159a2ae2c59f9270ac8e42676e6eb0fb7c36&token=03428626b23f5728f96bb58ff9bcf4bcb04f8ea258b07ed9fa69d8dd94b46b40"

# ── 지역 분류 규칙 ────────────────────────────────────────────────────────
DEST_RULES = [
    # destination → (countries 키워드, portRoute 키워드)
    ('south-america', 
     ['Brazil','Argentina','Peru','Chile','Ecuador','Colombia','Uruguay','Venezuela','Bolivia','Paraguay'],
     ['Buenos Aires','Rio de Janeiro','Valparaíso','Cartagena','Lima','Santiago','Montevideo','Ushuaia','Amazon']),
    ('oceania',
     ['Australia','New Zealand','Vanuatu','New Caledonia','Fiji','Papua New Guinea','Solomon Islands','Tonga','Samoa'],
     ['Sydney','Melbourne','Auckland','Brisbane','Fremantle','Adelaide','Hobart','Noumea','Suva','Port Vila']),
    ('northern-europe',
     ['Norway','Iceland','Finland','Sweden','Denmark','Estonia','Latvia','Lithuania','Russia','Ireland'],
     ['Bergen','Oslo','Reykjavik','Helsinki','Stockholm','Copenhagen','Tallinn','Riga','Dublin','Southampton','Hamburg','Kiel']),
    ('mediterranean',
     ['Italy','Greece','Spain','Croatia','Malta','Montenegro','Turkey','Tunisia','Morocco','Cyprus','France','Portugal','Slovenia'],
     ['Barcelona','Rome','Civitavecchia','Athens','Piraeus','Dubrovnik','Split','Valletta','Kotor','Marseille','Nice','Cannes','Palma','Lisbon','Porto']),
    ('caribbean',
     ['Bahamas','Jamaica','Barbados','Trinidad','Grenada','Saint Lucia','Martinique','Guadeloupe','Dominica','Saint Kitts','Antigua','Curaçao','Aruba','Belize','Honduras'],
     ['Nassau','Ocho Rios','Bridgetown','St. George','Castries','Fort-de-France','Roseau','Basseterre','St. John\'s','Willemstad','Oranjestad','Belize City']),
    ('asia',
     ['United Arab Emirates','Oman','Bahrain','Qatar','Kuwait','Jordan','Israel','Egypt','India','Sri Lanka','Maldives'],
     ['Dubai','Abu Dhabi','Muscat','Salalah','Aqaba','Haifa','Alexandria','Mumbai','Colombo','Malé','Doha']),
    ('southeast-asia',
     ['Singapore','Thailand','Vietnam','Malaysia','Indonesia','Philippines','Cambodia','Myanmar'],
     ['Singapore','Bangkok','Ho Chi Minh','Danang','Kuala Lumpur','Penang','Bali','Benoa','Manila','Phuket','Sihanoukville']),
    ('alaska',
     ['United States','Canada'],  # ports 기반
     ['Ketchikan','Juneau','Skagway','Sitka','Hubbard Glacier','Glacier Bay','Whittier','Seward','Homer','Kodiak','Yakutat','Haines','Wrangell','Tracy Arm','Endicott Arm','College Fjord']),
    ('hawaii',
     ['United States'],
     ['Honolulu','Lahaina','Kahului','Nawiliwili','Kailua-Kona','Hilo','Maui','Kauai']),
    ('africa',
     ['South Africa','Mozambique','Kenya','Tanzania','Seychelles','Mauritius','Madagascar','Réunion','Cape Verde','Senegal','Ghana'],
     ['Cape Town','Durban','Mombasa','Zanzibar','Mahé','Port Louis','Walvis Bay','Dakar','Accra']),
    ('canary-islands',
     ['Spain','Portugal'],
     ['Las Palmas','Tenerife','Lanzarote','Fuerteventura','Funchal','Madeira','Arrecife','Santa Cruz de Tenerife','Gran Canaria','La Palma','Agadir','Casablanca']),
    ('transatlantic',
     [],
     ['Transatlantic','Southampton','New York','Fort Lauderdale','Lisbon','Barcelona','Civitavecchia']),
]

def classify_destination(cruise):
    """portRoute + countries 기반으로 destination 분류"""
    route = (cruise.get('portRoute') or '').lower()
    countries = [c.lower() for c in (cruise.get('countries') or [])]
    
    for dest, country_kws, port_kws in DEST_RULES:
        # 항구 키워드 우선 (더 정확)
        if any(p.lower() in route for p in port_kws):
            return dest
        # 국가 키워드 (항구 없을 때)
        if country_kws and any(c.lower() in countries for c in country_kws):
            return dest
    return 'other'

print("Loading cruises.json...")
with open(CRUISES_FILE, encoding='utf-8') as f:
    data = json.load(f)

print(f"Total: {len(data)}개")

# ── Step 1: 'other' 재분류 ────────────────────────────────────────────────
reclassified = 0
dest_changes = Counter()
for c in data:
    if c.get('destination') == 'other':
        new_dest = classify_destination(c)
        if new_dest != 'other':
            dest_changes[new_dest] += 1
            c['destination'] = new_dest
            reclassified += 1

print(f"\nStep 1 - 재분류 완료: {reclassified}개")
for d, cnt in sorted(dest_changes.items(), key=lambda x: -x[1]):
    print(f"  other → {d}: {cnt}개")

# ── Step 2: Princess API 재수집 ───────────────────────────────────────────
princess_no_route = [c for c in data if c.get('operator') == 'Princess Cruises' and not c.get('portRoute')]
print(f"\nStep 2 - Princess portRoute 없는 상품: {len(princess_no_route)}개")
print("Widgety API에서 재수집 시작...")

def fetch_holiday(ref):
    url = f"https://www.widgety.co.uk/api/holidays/dates/{ref}.json?{API_AUTH}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read())
    except Exception as e:
        return None

princess_updated = 0
princess_failed = 0

for i, c in enumerate(princess_no_route):
    ref = c.get('ref','')
    if not ref:
        continue

    data_holiday = fetch_holiday(ref)
    if data_holiday and data_holiday.get('status') != 404:
        # starts_at, ends_at
        starts = data_holiday.get('starts_at') or {}
        ends = data_holiday.get('ends_at') or {}
        starts_name = starts.get('name','') if isinstance(starts, dict) else ''
        ends_name = ends.get('name','') if isinstance(ends, dict) else ''

        # itinerary ports
        itin = data_holiday.get('itinerary', {})
        days = itin.get('days', []) if isinstance(itin, dict) else []
        ports = []
        for day in days:
            for loc in (day.get('locations') or []):
                name = loc.get('name','')
                if name and name not in ports:
                    ports.append(name)

        if ports:
            c['portRoute'] = ' → '.join(ports[:6])
            if starts_name:
                c['startsAt'] = {'name': starts_name, 'nameKo': starts_name, 'country': starts.get('country',''), 'countryKo': starts.get('country','')}
            if ends_name:
                c['endsAt'] = {'name': ends_name, 'nameKo': ends_name, 'country': ends.get('country',''), 'countryKo': ends.get('country','')}
            c['ports'] = [{'name': p, 'nameKo': p} for p in ports]
            # destination 재분류
            if c.get('destination') == 'other' or not c.get('destination'):
                c['destination'] = classify_destination(c)
            princess_updated += 1
            if i % 50 == 0:
                print(f"  [{i}/{len(princess_no_route)}] {ref} → {c.get('portRoute','')[:60]}")
        else:
            princess_failed += 1
    else:
        princess_failed += 1

    time.sleep(0.8)

print(f"\nPrincess 업데이트: {princess_updated}개, 실패: {princess_failed}개")

# ── 저장 ──────────────────────────────────────────────────────────────────
print("\nSaving cruises.json...")
with open(CRUISES_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

print("\n=== 최종 destination 분포 ===")
from collections import Counter
today = '2026-03-26'
future = [c for c in data if c.get('dateFrom','') >= today]
dests = Counter(c.get('destination','') for c in future)
for d, cnt in sorted(dests.items(), key=lambda x: -x[1]):
    print(f"  {d}: {cnt}개")
print(f"  총: {len(future)}개")
print("SCRIPT DONE")
