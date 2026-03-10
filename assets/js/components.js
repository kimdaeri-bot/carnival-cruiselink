// Shared components - Hybrid version
const Components = {
  // active: 'home'|'dest'|'ships'|'guide' / base: '' (root) or '../../' (2depth subdir)
  header(active = 'home', base = '') {
    return `
    <header class="header">
      <div class="container">
        <a href="${base}index.html" class="logo"><img src="${base}assets/images/logo.png" alt="크루즈링크" style="height:36px"></a>
        <nav class="nav" id="mainNav">
          <a href="${base}index.html" class="${active === 'home' ? 'active' : ''}">홈</a>
          <a href="${base}destinations.html" class="${active === 'dest' ? 'active' : ''}">목적지</a>
          <a href="${base}ships.html" class="${active === 'ships' ? 'active' : ''}">선사소개</a>
          <a href="${base}promotions.html" class="${active === 'promo' ? 'active' : ''}">프로모션</a>
          <a href="${base}guide/" class="${active === 'guide' ? 'active' : ''}">크루즈 가이드</a>
          <a href="https://pf.kakao.com/_xgYbJG" target="_blank" class="${active === 'contact' ? 'active' : ''}">문의</a>
        </nav>
        <a href="tel:02-3788-9119" class="header-phone">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
          02-3788-9119
        </a>
        <button class="mobile-menu-btn" onclick="document.getElementById('mainNav').classList.toggle('open')">☰</button>
      </div>
    </header>`;
  },

  footer(base = '') {
    return `
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-col">
            <h4>크루즈링크는?</h4>
            <p><a href="${base}about.html">회사소개</a></p>
            <p><a href="${base}newsletter.html">📬 뉴스레터 구독</a></p>
            <p><a href="${base}privacy.html">개인정보 처리방침</a></p>
            <p><a href="${base}terms.html">이용약관</a></p>
          </div>
          <div class="footer-col">
            <h4>연락처 정보</h4>
            <p>📞 <a href="tel:02-3788-9119">02-3788-9119</a></p>
            <p>💬 <a href="https://pf.kakao.com/_xgYbJG" target="_blank">카카오톡 상담</a></p>
            <p>✉️ <a href="mailto:info@cruiselink.co.kr">info@cruiselink.co.kr</a></p>
          </div>
          <div class="footer-col">
            <h4>크루즈 가이드</h4>
            <p><a href="${base}guide/">가이드 홈</a></p>
            <p><a href="${base}guide/cruise-lines/">선사 소개</a></p>
            <p><a href="${base}guide/ships/">선박 소개</a></p>
            <p><a href="${base}guide/ports/">기항지 가이드</a></p>
            <p><a href="${base}guide/news/">크루즈 뉴스</a></p>
            <p><a href="${base}guide/tips/">크루즈 실전 팁</a></p>
          </div>
          <div class="footer-col">
            <h4>목적지</h4>
            <p><a href="${base}destinations.html">목적지 가이드</a></p>
            <p><a href="${base}destination.html?dest=korea">한국/일본</a></p>
            <p><a href="${base}destination.html?dest=mediterranean">지중해</a></p>
            <p><a href="${base}destination.html?dest=alaska">알래스카</a></p>
            <p><a href="${base}destination.html?dest=caribbean">카리브해</a></p>
          </div>
        </div>
        <div class="footer-bottom" style="font-size:0.8rem;line-height:1.6;color:var(--gray-500)">
          <p>서울특별시 강서구 마곡서로 152, 두산 더 랜드타워 5층</p>
          <p>아남항공 주식회사(크루즈링크) | 대표: 김영성 | 사업자 등록번호: 104-81-84918</p>
          <p style="margin-top:8px">© ${new Date().getFullYear()} 크루즈링크. All rights reserved.</p>
        </div>
      </div>
    </footer>`;
  },

  ctaSection() {
    return `
    <section class="cta-section">
      <div class="container">
        <h2>크루즈 여행, 지금 상담하세요</h2>
        <p>전문 상담원이 최적의 크루즈를 찾아드립니다</p>
        <div class="cta-buttons cta-three">
          <a href="https://pf.kakao.com/_xgYbJG" target="_blank" class="btn btn-orange">💬 카카오톡 상담</a>
          <a href="tel:02-3788-9119" class="btn btn-white">📞 02-3788-9119</a>
          <button class="btn btn-white-solid" onclick="openInquiry()">📋 온라인 문의</button>
        </div>
      </div>
    </section>`;
  },

  loading() {
    return `<div class="loading"><div class="loading-spinner"></div><p>크루즈 정보를 불러오는 중...</p></div>`;
  },

  // Local JSON cruise card (for index/destination/ships pages)
  localCruiseCard(c) {
    const fromPrice = c.priceBalcony || c.priceOutside || c.priceInside;
    const region = c.regions?.[0] || '';
    return `
    <div class="cruise-card" onclick="location.href='cruise-view.html?ref=${c.ref}'">
      <div class="cruise-card-img">
        <img src="${c.image}" alt="${c.shipTitle}" loading="lazy" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 200%22><rect fill=%22%23e0e0e0%22 width=%22400%22 height=%22200%22/><text x=%2250%%22 y=%2250%%22 fill=%22%239e9e9e%22 text-anchor=%22middle%22 dy=%22.3em%22 font-size=%2220%22>🚢</text></svg>'">
        ${region ? `<span class="cruise-card-tag">${Translations.regionName(region)}</span>` : ''}
      </div>
      <div class="cruise-card-body">
        <div class="cruise-card-operator">${Translations.operatorName(c.operator)} · ${c.shipTitleKo || Translations.shipName(c.shipTitle)}</div>
        <div class="cruise-card-title">${c.title}</div>
        <div class="cruise-card-route">${c.portRouteKo || c.portRoute}</div>
        <div class="cruise-card-meta">
          <span class="cruise-card-date">📅 ${API.formatDate(c.dateFrom)} · ${c.nights}박</span>
          <span class="cruise-card-price">${API.formatPrice(fromPrice, c.currency)}</span>
        </div>
        <a href="cruise-view.html?ref=${c.ref}" class="cruise-card-btn">자세히 보기</a>
      </div>
    </div>`;
  },

  // Local JSON cruise list item
  localCruiseItem(c) {
    const fromPrice = c.priceBalcony || c.priceOutside || c.priceInside;
    const region = c.regions?.[0] || '';
    return `
    <div class="cruise-item">
      <div class="cruise-item-img">
        <img src="${c.image}" alt="${c.shipTitle}" loading="lazy" onerror="this.style.display='none'">
        ${region ? `<span class="cruise-item-tag">${Translations.regionName(region)}</span>` : ''}
      </div>
      <div class="cruise-item-body">
        <div class="cruise-item-operator">${Translations.operatorName(c.operator)} · ${c.shipTitleKo || Translations.shipName(c.shipTitle)}</div>
        <div class="cruise-item-title">${c.title}</div>
        <div class="cruise-item-route">🚢 ${Translations.portRoute(c.portRouteKo || c.portRoute)}</div>
        <div class="cruise-item-hashtags">${(c.hashtags||[]).map(t => {
          if (!/[\uAC00-\uD7A3]/.test(t) && t.startsWith('#')) {
            const raw = t.slice(1);
            const ship = Translations.shipName(raw);
            if (ship !== raw) return `<span>#${ship}</span>`;
            const port = Translations.portName(raw);
            if (port !== raw) return `<span>#${port}</span>`;
            return ''; // 번역 불가 영문 태그 제거
          }
          return `<span>${t}</span>`;
        }).filter(Boolean).join('')}</div>
        <div class="cruise-item-footer">
          <div>
            <div class="cruise-item-date">📅 ${API.formatDate(c.dateFrom)} ~ ${API.formatDate(c.dateTo)} · ${c.nights}박</div>
            <div class="cruise-item-price">${API.formatPrice(fromPrice, c.currency)} <small style="font-weight:400;font-size:0.8rem;color:#888">/1인</small></div>
          </div>
          <div class="cruise-item-actions">
            <a href="cruise-view.html?ref=${c.ref}" class="btn btn-navy btn-sm">상세보기</a>
            <button class="btn btn-orange btn-sm" onclick="openInquiryWith('${(c.title||'').replace(/'/g,"\\'")}','${(c.operator||'').replace(/'/g,"\\'")}','${(c.shipTitleKo || Translations.shipName(c.shipTitle)||'').replace(/'/g,"\\'")}','${c.dateFrom||''}','${c.nights||''}','${String(fromPrice||'')}','${c.ref||''}','${c.currency||''}')">문의하기</button>
          </div>
        </div>
      </div>
    </div>`;
  },

  // Legacy: Live API cruise card (for cruise-view.html)
  cruiseCard(holiday, shipInfo) {
    const price = holiday.headline_prices?.cruise?.double;
    const fromPrice = price?.from_balcony || price?.from_inside || price?.from_outside;
    const route = API.shortRoute(holiday.itinerary, 4);
    const region = holiday.regions?.[0] || '';
    const img = shipInfo?.coverImage || holiday.images?.[0]?.href || '';
    return `
    <div class="cruise-card" onclick="location.href='cruise-view.html?ref=${holiday.date_ref}'">
      <div class="cruise-card-img">
        <img src="${img}" alt="${holiday.ship_title}" loading="lazy" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 200%22><rect fill=%22%23e0e0e0%22 width=%22400%22 height=%22200%22/><text x=%2250%%22 y=%2250%%22 fill=%22%239e9e9e%22 text-anchor=%22middle%22 dy=%22.3em%22 font-size=%2220%22>🚢</text></svg>'">
        ${region ? `<span class="cruise-card-tag">${Translations.regionName(region)}</span>` : ''}
      </div>
      <div class="cruise-card-body">
        <div class="cruise-card-operator">${Translations.operatorName(holiday.operator_title || shipInfo?.operator || '')} · ${Translations.shipName(holiday.ship_title || '')}</div>
        <div class="cruise-card-title">${Translations.portName(holiday.starts_at?.name || '')} 출발 ${holiday.cruise_nights || holiday.duration_days || ''}박 크루즈</div>
        <div class="cruise-card-route">${route}</div>
        <div class="cruise-card-meta">
          <span class="cruise-card-date">📅 ${API.formatDate(holiday.date_from)} · ${holiday.cruise_nights || holiday.duration_days || ''}박</span>
          <span class="cruise-card-price">${API.formatPrice(fromPrice)} <small style="font-weight:normal;font-size:.8em;opacity:.8">/1인</small></span>
        </div>
        <a href="cruise-view.html?ref=${holiday.date_ref}" class="cruise-card-btn">자세히 보기</a>
      </div>
    </div>`;
  },

  cruiseItem(holiday, shipInfo) {
    const price = holiday.headline_prices?.cruise?.double;
    const fromPrice = price?.from_balcony || price?.from_inside || price?.from_outside;
    const route = API.shortRoute(holiday.itinerary, 5);
    const region = holiday.regions?.[0] || '';
    const img = shipInfo?.coverImage || holiday.images?.[0]?.href || '';
    const tags = API.hashtags(holiday);
    return `
    <div class="cruise-item">
      <div class="cruise-item-img">
        <img src="${img}" alt="${holiday.ship_title}" loading="lazy" onerror="this.style.display='none'">
        ${region ? `<span class="cruise-item-tag">${Translations.regionName(region)}</span>` : ''}
      </div>
      <div class="cruise-item-body">
        <div class="cruise-item-operator">${Translations.operatorName(holiday.operator_title || '')} · ${Translations.shipName(holiday.ship_title || '')}</div>
        <div class="cruise-item-title">${Translations.portName(holiday.starts_at?.name || '')} 출발 ${holiday.cruise_nights || holiday.duration_days || ''}박 크루즈</div>
        <div class="cruise-item-route">🚢 ${route}</div>
        <div class="cruise-item-hashtags">${tags.map(t => `<span>${t}</span>`).join('')}</div>
        <div class="cruise-item-footer">
          <div>
            <div class="cruise-item-date">📅 ${API.formatDate(holiday.date_from)} ~ ${API.formatDate(holiday.date_to)} · ${holiday.cruise_nights || holiday.duration_days || ''}박</div>
            <div class="cruise-item-price">${API.formatPrice(fromPrice)} <small style="font-weight:400;font-size:0.8rem;color:#888">/1인</small></div>
          </div>
          <div class="cruise-item-actions">
            <a href="cruise-view.html?ref=${holiday.date_ref}" class="btn btn-navy btn-sm">상세보기</a>
            <button class="btn btn-orange btn-sm" onclick="openInquiryWith('${(Translations.portName(holiday.starts_at?.name||'')+' 출발 '+(holiday.cruise_nights||holiday.duration_days||'')+'박 크루즈').replace(/'/g,"\\'")}','${(holiday.operator_title||'').replace(/'/g,"\\'")}','${(holiday.ship_title||'').replace(/'/g,"\\'")}','${holiday.date_from||''}','${holiday.cruise_nights||holiday.duration_days||''}','${String(fromPrice||'')}','${holiday.date_ref||''}','')">문의하기</button>
          </div>
        </div>
      </div>
    </div>`;
  },

  // 가이드 페이지 공유 바
  shareBar() {
    return `
    <div id="guideShareBar" style="position:fixed;bottom:0;left:0;right:0;z-index:900;background:#fff;border-top:1px solid #e0e0e0;padding:10px 16px;display:flex;align-items:center;justify-content:space-between;gap:10px;box-shadow:0 -2px 12px rgba(0,0,0,.08)">
      <span style="font-size:13px;color:#555;font-weight:500;flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis" id="gsb-title"></span>
      <div style="display:flex;gap:8px;flex-shrink:0">
        <button onclick="Components.doShare('kakao')" style="display:flex;align-items:center;gap:5px;background:#FEE500;color:#191919;border:none;padding:8px 14px;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3C6.477 3 2 6.477 2 10.909c0 2.804 1.635 5.268 4.1 6.8l-.82 3.02a.3.3 0 0 0 .44.34l3.54-2.33c.89.12 1.81.18 2.74.18 5.523 0 10-3.477 10-7.909S17.523 3 12 3z"/></svg>
          카카오
        </button>
        <button onclick="Components.doShare('copy')" style="display:flex;align-items:center;gap:5px;background:#1a237e;color:#fff;border:none;padding:8px 14px;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H8V7h11v14z"/></svg>
          링크복사
        </button>
        <button onclick="Components.doShare('native')" style="display:flex;align-items:center;gap:5px;background:#ff6f00;color:#fff;border:none;padding:8px 14px;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/></svg>
          공유
        </button>
      </div>
    </div>
    <div style="height:58px"></div>
    <div id="gsbToast" style="display:none;position:fixed;bottom:72px;left:50%;transform:translateX(-50%);background:#1a2540;color:#fff;padding:9px 22px;border-radius:20px;font-size:13px;font-weight:600;z-index:9999;white-space:nowrap"></div>
    <script>
    (function(){
      // 제목 세팅
      var el = document.querySelector('h1');
      if(el) document.getElementById('gsb-title').textContent = el.innerText;

      // Kakao SDK 로드 (미로드 시)
      if(typeof Kakao === 'undefined'){
        var s = document.createElement('script');
        s.src = 'https://t1.kakaocdn.net/kakao_js_sdk/2.7.2/kakao.min.js';
        s.onload = function(){
          if(!Kakao.isInitialized()) Kakao.init('52a3a4296f48da88499c83f3be0312ef');
        };
        document.head.appendChild(s);
      } else if(!Kakao.isInitialized()){
        Kakao.init('52a3a4296f48da88499c83f3be0312ef');
      }
    })();
    </script>`;
  },

  doShare(type) {
    const url = location.href;
    const title = (document.querySelector('h1') || {innerText: document.title}).innerText;

    if (type === 'native' && navigator.share) {
      navigator.share({ title: '🚢 ' + title, url }).catch(() => {});
      return;
    }
    if (type === 'kakao') {
      try {
        if (typeof Kakao !== 'undefined' && Kakao.isInitialized()) {
          Kakao.Share.sendDefault({
            objectType: 'feed',
            content: {
              title: title,
              description: '크루즈링크에서 확인하세요',
              imageUrl: 'https://www.cruiselink.co.kr/assets/images/og-default.jpg',
              link: { mobileWebUrl: url, webUrl: url }
            },
            buttons: [{ title: '자세히 보기', link: { mobileWebUrl: url, webUrl: url } }]
          });
          return;
        }
      } catch(e) {}
      window.open('https://pf.kakao.com/_xgYbJG', '_blank');
      return;
    }
    // 링크복사 or native fallback
    navigator.clipboard.writeText(url).then(() => {
      Components._gsbToast('🔗 링크가 복사됐습니다!');
    }).catch(() => {
      const ta = document.createElement('textarea');
      ta.value = url; document.body.appendChild(ta);
      ta.select(); document.execCommand('copy');
      document.body.removeChild(ta);
      Components._gsbToast('🔗 링크가 복사됐습니다!');
    });
  },

  _gsbToast(msg) {
    const t = document.getElementById('gsbToast');
    if (!t) return;
    t.textContent = msg; t.style.display = 'block';
    setTimeout(() => t.style.display = 'none', 2200);
  },
};
