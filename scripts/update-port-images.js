// cruises-mini.json 각 항목에 portImage 추가
// holiday itinerary에서 기항지 이미지 수집 (겹치지 않게)

const https = require('https');
const fs = require('fs');
const path = require('path');

const AUTH = 'app_id=fdb0159a2ae2c59f9270ac8e42676e6eb0fb7c36&token=03428626b23f5728f96bb58ff9bcf4bcb04f8ea258b07ed9fa69d8dd94b46b40';
const BASE = 'https://www.widgety.co.uk/api';
const MINI_PATH = path.join(__dirname, '../assets/data/cruises-mini.json');

function get(url) {
  return new Promise((resolve) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve(null); }
      });
    }).on('error', () => resolve(null));
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  const cruises = JSON.parse(fs.readFileSync(MINI_PATH, 'utf8'));
  const usedImages = new Set();

  // 각 크루즈의 holiday itinerary에서 기항지 이미지 수집
  for (let i = 0; i < cruises.length; i++) {
    const c = cruises[i];
    console.log(`[${i+1}/${cruises.length}] ${c.ref} (${c.destination})`);

    const holiday = await get(`${BASE}/holidays/dates/${c.ref}.json?${AUTH}`);
    await sleep(300);

    if (!holiday || !holiday.itinerary?.days) {
      console.log('  → holiday 없음, 스킵');
      continue;
    }

    // 기항지 이미지 수집 (바다 항해일 제외)
    const portImages = [];
    for (const day of holiday.itinerary.days) {
      if (day.day_type?.includes('SEA')) continue;
      const loc = day.locations?.[0];
      if (!loc) continue;
      const imgs = (loc.widgety_data?.images || []).filter(img => img?.href);
      for (const img of imgs) {
        if (!usedImages.has(img.href)) {
          portImages.push({ href: img.href, port: loc.name });
        }
      }
      if (portImages.length >= 3) break;
    }

    if (portImages.length > 0) {
      // 가장 첫 번째 미사용 이미지 사용
      const chosen = portImages[0];
      usedImages.add(chosen.href);
      c.portImage = chosen.href;
      c.portImagePort = chosen.port;
      console.log(`  → ${chosen.port}: ${chosen.href.slice(0,60)}...`);
    } else {
      console.log('  → 기항지 이미지 없음');
    }
  }

  fs.writeFileSync(MINI_PATH, JSON.stringify(cruises, null, 2));
  console.log('\n✅ cruises-mini.json 업데이트 완료');
  
  // 결과 요약
  const withPortImg = cruises.filter(c => c.portImage).length;
  console.log(`portImage 있는 항목: ${withPortImg}/${cruises.length}`);
}

main().catch(console.error);
