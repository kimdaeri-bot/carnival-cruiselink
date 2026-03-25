#!/usr/bin/env python3
"""
cruises.json의 ports 배열에 해상일(at sea) 삽입
- nights + 1 = 총 일수
- ports = 기항지 목록 (해상일 제외)
- 차이만큼 해상일을 기항지 사이에 균등 배분
"""
import json, math

BASE = "/Users/kim/.openclaw/workspace/cruiselink-v2"
CRUISES_FILE = f"{BASE}/assets/data/cruises.json"

SEA_PORT = {"name": "At Sea", "nameKo": "해상 항해"}

def insert_sea_days(ports, nights):
    """
    ports 배열에 해상일을 삽입해서 반환.
    전략: 첫 기항지 = day1, 나머지 기항지 사이에 해상일 균등 배분,
          끝에 남는 해상일은 마지막 기항지 다음에 배치
    """
    total_days = nights + 1  # 출발일 포함 (ex: 4박 = 5일)
    sea_count = total_days - len(ports)
    if sea_count <= 0:
        return ports  # 해상일 없음

    result = []
    n_ports = len(ports)

    if n_ports == 0:
        # 기항지 없으면 전부 해상일
        return [SEA_PORT] * total_days

    if n_ports == 1:
        # 기항지 1개: 첫날 기항지, 나머지 해상
        result.append(ports[0])
        result.extend([SEA_PORT] * sea_count)
        return result

    # 기항지 n개 사이에 (n-1)개 구간 존재
    # 각 구간에 해상일을 균등 배분, 남는 건 첫 구간에 배치
    result.append(ports[0])
    remaining_sea = sea_count
    remaining_ports = n_ports - 1  # 아직 배치 안 한 기항지 수

    for i in range(1, n_ports):
        # 이 구간에 배분할 해상일 수
        sea_here = math.ceil(remaining_sea / remaining_ports)
        for _ in range(sea_here):
            result.append(SEA_PORT)
        remaining_sea -= sea_here
        remaining_ports -= 1
        result.append(ports[i])

    # 남은 해상일 (뒤에 추가)
    for _ in range(remaining_sea):
        result.append(SEA_PORT)

    return result


print("Loading cruises.json...")
with open(CRUISES_FILE, encoding='utf-8') as f:
    data = json.load(f)

print(f"Total cruises: {len(data)}")

updated = 0
skipped = 0
for c in data:
    nights = c.get('nights', 0)
    ports = c.get('ports', [])
    total_days = nights + 1
    sea_count = total_days - len(ports)

    if sea_count <= 0:
        skipped += 1
        continue

    # 이미 해상일 포함돼 있는지 체크
    if any(p.get('name', '') in ('At Sea', '해상 항해') for p in ports):
        skipped += 1
        continue

    new_ports = insert_sea_days(ports, nights)
    c['ports'] = new_ports

    # portRoute도 업데이트 (해상일 제외한 기항지만 표시)
    port_names = [p.get('nameKo', p.get('name', '')) for p in new_ports if p.get('name') not in ('At Sea',)]
    # 중복 제거 (첫 등장만)
    seen = []
    for pn in port_names:
        if pn not in seen:
            seen.append(pn)
    c['portRoute'] = ' → '.join(seen)

    updated += 1

print(f"Updated: {updated} cruises")
print(f"Skipped (no sea days): {skipped}")

print("Saving...")
with open(CRUISES_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

print(f"Done. File saved.")
print("SCRIPT DONE")
