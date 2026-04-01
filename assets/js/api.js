// CruiseLink V2 - Hybrid API (Local JSON + Live API) v2026-03-28
const API = {
  base: 'https://www.widgety.co.uk/api',
  auth: 'app_id=fdb0159a2ae2c59f9270ac8e42676e6eb0fb7c36&token=03428626b23f5728f96bb58ff9bcf4bcb04f8ea258b07ed9fa69d8dd94b46b40',
  cache: {},

  url(endpoint, params = '') {
    const sep = endpoint.includes('?') ? '&' : '?';
    return `${this.base}/${endpoint}${sep}${this.auth}${params ? '&' + params : ''}`;
  },

  async fetch(endpoint, params = '') {
    const key = endpoint + params;
    if (this.cache[key]) return this.cache[key];
    try {
      const res = await fetch(this.url(endpoint, params));
      if (!res.ok) throw new Error(`API ${res.status}`);
      const data = await res.json();
      this.cache[key] = data;
      return data;
    } catch (e) {
      console.error('API Error:', e);
      return null;
    }
  },

  // ===== LOCAL JSON (목록/검색/필터용) =====

  _localShips: null,
  _destCache: {},   // 목적지별 캐시
  _featuredCache: null,

  async loadLocalShips() {
    if (this._localShips) return this._localShips;
    try {
      const res = await fetch('https://kimdaeri-bot.github.io/carnival-cruiselink/assets/data/ships.json');
      this._localShips = await res.json();
    } catch { this._localShips = []; }
    return this._localShips;
  },

  // 목적지별 파일 로드 (없으면 전체 파일 폴백)
  // 탭 전용 미니 캐시 (58KB — 목적지별 top6)
  _miniCache: null,
  async getMiniCruises(dest, limit = 5) {
    if (!this._miniCache) {
      try {
        const res = await fetch('https://kimdaeri-bot.github.io/carnival-cruiselink/assets/data/cruises-mini.json');
        const all = res.ok ? await res.json() : [];
        // MSC 전용 사이트 — MSC만 필터
        this._miniCache = all.filter(c => (c.operator || '').toLowerCase().includes('carnival'));
      } catch { this._miniCache = []; }
    }
    const cutoff = (() => { const d = new Date(); d.setMonth(d.getMonth() + 2); return d.toISOString().slice(0, 10); })();
    return this._miniCache
      .filter(c => (!dest || c.destination === dest) && c.dateFrom >= cutoff)
      .slice(0, limit);
  },

  async loadCruisesByDest(dest) {
    if (this._destCache[dest]) return this._destCache[dest];
    try {
      const res = await fetch(`https://kimdaeri-bot.github.io/carnival-cruiselink/assets/data/cruises-${dest}.json`);
      if (!res.ok) throw new Error('no split file');
      const data = await res.json();
      this._destCache[dest] = data;
      return data;
    } catch {
      // 분할 파일 없으면 전체 파일에서 필터
      const all = await this.loadAllCruises();
      const filtered = all.filter(c => c.destination === dest);
      this._destCache[dest] = filtered;
      return filtered;
    }
  },

  // 전체 cruises.json (폴백용 — 분할 파일 있으면 사용 안 함)
  _allCruisesCache: null,
  async loadAllCruises() {
    if (this._allCruisesCache) return this._allCruisesCache;
    try {
      const res = await fetch('https://kimdaeri-bot.github.io/carnival-cruiselink/assets/data/cruises.json');
      const all = await res.json();
      // MSC 전용 사이트 — MSC Cruises만 필터링
      this._allCruisesCache = all.filter(c => (c.operator || '').toLowerCase().includes('carnival'));
    } catch { this._allCruisesCache = []; }
    return this._allCruisesCache;
  },

  // 레거시 호환 (cruise-view/ 등에서 사용)
  async loadLocalCruises() {
    return this.loadAllCruises();
  },

  // Filter local cruises — dest 지정 시 분할 파일 로드
  async filterCruises({ dest, operator, operators, ports, month, duration, limit, minDate, maxDate } = {}) {
    // dest 있으면 해당 목적지 파일만 로드
    const cruises = dest ? await this.loadCruisesByDest(dest) : await this.loadAllCruises();
    const now = minDate || new Date().toISOString().slice(0, 10);
    return cruises.filter(c => {
      if (c.dateFrom < now) return false;
      if (maxDate && c.dateFrom > maxDate) return false;
      if (dest && c.destination !== dest) return false;
      // Multi-select operators
      if (operators?.length > 0 && !operators.some(op => c.operator?.includes(op))) return false;
      // Legacy single operator
      if (operator && !operators?.length && !c.operator?.includes(operator)) return false;
      // Multi-select departure ports (한/영 양방향 매칭)
      if (ports?.length > 0) {
        const startEn = (c.startsAt?.name || '').toLowerCase();
        const startKo = (c.startsAt?.nameKo || (typeof Translations !== 'undefined' ? Translations.portName(c.startsAt?.name||'') : '') || '');
        const startEnBase = startEn.split(',')[0].trim(); // "miami, florida" → "miami"
        if (!ports.some(p => {
          const pL = p.toLowerCase();
          const pEn = (typeof Translations !== 'undefined' ? Translations.portName(p) : p).toLowerCase();
          return startKo.includes(p) || startEn.includes(pL) || startEnBase.includes(pL) ||
                 (pEn !== pL && startEn.includes(pEn));
        })) return false;
      }
      if (month) {
        const cm = c.dateFrom.slice(0, 7);
        if (cm !== month) return false;
      }
      if (duration === 'short' && c.nights > 5) return false;
      if (duration === 'medium' && (c.nights < 6 || c.nights > 10)) return false;
      if (duration === 'long' && c.nights < 11) return false;
      return true;
    }); // limit 없으면 전체 반환
  },

  // 추천 크루즈 — featured.json (극소용량) 로드
  async getRecommendedCruises(count = 9) {
    if (!this._featuredCache) {
      try {
        const res = await fetch('https://kimdaeri-bot.github.io/carnival-cruiselink/assets/data/featured.json');
        if (res.ok) {
          this._featuredCache = await res.json();
        } else {
          throw new Error('no featured.json');
        }
      } catch {
        // 폴백: 전체 파일에서 FEATURED_REFS 추출
        const FEATURED_REFS = [
          'MSCBE20260510TYOTYO','NCLENC-20260503-07-SEA-SEA','MSCEU20260417BCNBCN',
          'MSCAM20260418MIAMIA','MSCER20260502KELKEL','MSCEU20261128DXBDXB',
          'NCLAME-20260502-07-HNL-HNL','NCLJOY-20260425-18-MIA-SEA','NCLSPR-20261212-11-SYD-SYD',
        ];
        const all = await this.loadAllCruises();
        const refMap = {};
        all.forEach(c => { refMap[c.ref] = c; });
        this._featuredCache = FEATURED_REFS.map(r => refMap[r]).filter(Boolean);
      }
    }
    const today = new Date().toISOString().slice(0, 10);
    return this._featuredCache.filter(c => c && c.dateFrom >= today).slice(0, count);
  },

  _featured2Cache: null,
  async getRecommendedCruises2(count = 12) {
    if (!this._featured2Cache) {
      try {
        const res = await fetch('https://kimdaeri-bot.github.io/carnival-cruiselink/assets/data/featured2.json');
        if (res.ok) {
          this._featured2Cache = await res.json();
        } else { throw new Error('no featured2.json'); }
      } catch {
        // 폴백: mini에서 Explora 필터
        const mini = await this.getMiniCruises(null, 999);
        this._featured2Cache = mini.filter(c => c.operatorShort === 'Explora');
      }
    }
    const cutoff = (() => { const d = new Date(); d.setMonth(d.getMonth() + 2); return d.toISOString().slice(0, 10); })();
    return this._featured2Cache.filter(c => c && c.dateFrom >= cutoff).slice(0, count);
  },

  // Get local ship by slug
  async getLocalShip(slug) {
    const ships = await this.loadLocalShips();
    return ships.find(s => s.slug === slug) || null;
  },

  // Get cruises for a specific ship
  async getShipCruises(shipSlug) {
    const cruises = await this.loadLocalCruises();
    const now = new Date().toISOString().slice(0, 10);
    return cruises.filter(c => c.shipSlug === shipSlug && c.dateFrom >= now);
  },

  // ===== LOCAL SHIP DETAILS =====
  _localShipDetails: null,

  async loadShipDetails() {
    if (this._localShipDetails) return this._localShipDetails;
    try {
      const res = await fetch('https://kimdaeri-bot.github.io/carnival-cruiselink/assets/data/ships-detail.json');
      const arr = await res.json();
      this._localShipDetails = {};
      arr.forEach(s => { this._localShipDetails[s.slug] = s; });
    } catch { this._localShipDetails = {}; }
    return this._localShipDetails;
  },

  async getShipDetail(slug) {
    const details = await this.loadShipDetails();
    return details[slug] || null;
  },

  // ===== LIVE API (상세 페이지 전용) =====

  // 선박 상세 (시설/덱플랜/객실 = 라이브)
  async getShipLive(slug) {
    return await this.fetch(`ships/${slug}.json`);
  },

  // 크루즈 상세 (일정, 가격, 기항지 이미지 = 라이브)
  async getHoliday(ref) {
    const data = await this.fetch(`holidays/dates/${ref}.json`);
    if (!data) return null;
    // 구 포맷: { holiday: {...} } / 신 포맷: { date_ref, ship_title, ... } (최상위)
    if (data.holiday) return data.holiday;
    if (data.date_ref || data.ship_title || data.operator_title) return data;
    return null;
  },

  // 전체 선박 목록 (API, 폴백용)
  async getAllShips() {
    if (this.cache._allShips) return this.cache._allShips;
    const p1 = await this.fetch('ships.json', 'per_page=50');
    let ships = p1?.ships || [];
    if (p1?.total > 50) {
      const p2 = await this.fetch('ships.json', 'per_page=50&page=2');
      ships = ships.concat(p2?.ships || []);
    }
    this.cache._allShips = ships;
    return ships;
  },

  // ===== 유틸리티 =====

  parseDate(dateStr) {
    if (!dateStr) return null;
    // YYYY-MM-DD 형식은 UTC로 파싱되어 로컬 타임존에서 하루 밀림 방지
    if (/^\d{4}-\d{2}-\d{2}$/.test(String(dateStr))) {
      const [y, m, d] = String(dateStr).split('-').map(Number);
      return new Date(y, m - 1, d);
    }
    return new Date(dateStr);
  },

  formatDate(dateStr) {
    const d = this.parseDate(dateStr);
    if (!d) return '';
    return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
  },

  formatDateKo(dateStr) {
    const d = this.parseDate(dateStr);
    if (!d) return '';
    const months = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'];
    return `${d.getFullYear()}년 ${months[d.getMonth()]} ${d.getDate()}일`;
  },

  formatPrice(price, currency = 'USD') {
    if (!price) return '문의';
    const num = parseFloat(price);
    if (isNaN(num)) return '문의';
    const symbols = { USD: '$', GBP: '£', EUR: '€' };
    return `${symbols[currency] || '$'}${num.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}~`;
  },

  // 기항지 경로 (라이브 itinerary용)
  routeString(itinerary) {
    if (!itinerary?.days) return '';
    const ports = [];
    itinerary.days.forEach(d => {
      d.locations?.forEach(l => {
        if (l.name && !ports.includes(l.name)) ports.push(l.name);
      });
    });
    return ports.map(p => Translations.portName(p)).join(' → ');
  },

  shortRoute(itinerary, max = 5) {
    if (!itinerary?.days) return '';
    const ports = [];
    itinerary.days.forEach(d => {
      d.locations?.forEach(l => {
        if (l.name && !ports.includes(l.name)) ports.push(l.name);
      });
    });
    const shown = ports.slice(0, max).map(p => Translations.portName(p));
    if (ports.length > max) shown.push('...');
    return shown.join(' → ');
  },

  hashtags(holiday) {
    const tags = [];
    if (holiday.regions) holiday.regions.forEach(r => tags.push('#' + r.replace(/\s+/g, '')));
    if (holiday.operator_title) tags.push('#' + holiday.operator_title.replace(/\s+/g, ''));
    if (holiday.ship_title) tags.push('#' + holiday.ship_title.replace(/\s+/g, ''));
    return tags.slice(0, 5);
  },
};
// v1774709361
