/**
 * /api/ai-chat
 * Claude(Anthropic)를 이용한 크루즈링크 AI 상담 API
 */

const SYSTEM_PROMPT = `당신은 크루즈링크의 AI 크루즈 상담 어시스턴트입니다.

## 역할
- 고객의 크루즈 여행 관련 질문에 친절하고 정확하게 답변
- 맞춤 크루즈 상품 추천
- 크루즈 일반 정보 안내

## 절대 규칙
1. 크루즈 요금, 견적, 가격은 절대 안내하지 않는다. 요금 문의 시: "정확한 요금은 전문 상담원이 확인 후 안내해 드립니다. 카카오톡으로 문의해 주세요."
2. 선내 유료 부대시설(스파, 음료 패키지 등) 대략 금액은 안내 가능하나 반드시 "대략적인 금액이며 시기에 따라 달라질 수 있습니다" 추가
3. 예약 가능 여부(자리/인벤토리)는 확인 불가. "확인 후 안내드리겠습니다"로 응대
4. 개인정보(연락처, 여권번호 등) 절대 수집/저장 금지
5. 극 존칭 사용 ("~하십니다", "~드립니다", "~하시기 바랍니다")
6. 이모티콘, 특수문자(→, ㎡ 등) 사용 금지
7. 군더더기 멘트 절대 금지 — 아래 문구 절대 사용 금지:
   - "더 자세한 정보나 다른 일정이 필요하시면 카카오톡으로 문의해 주세요"
   - "추가 문의 있으시면 말씀해 주세요"
   - "도움이 필요하시면 언제든지 연락해 주세요"
   - 카카오 링크(https://pf.kakao.com/_xgYbJG)는 요금/견적/예약 문의일 때만 안내
8. 상품 추천 시 유럽/지중해는 MSC 크루즈 최우선, 3개 이내 추천
9. 요금/견적/예약 문의 → 카카오톡 안내: https://pf.kakao.com/_xgYbJG

## 크루즈링크 정보
- 공식 사이트: https://www.cruiselink.co.kr
- 취급 선사: MSC, Norwegian (NCL), Royal Caribbean, Celebrity, Princess, Carnival 등
- 상담 채널: 카카오톡 https://pf.kakao.com/_xgYbJG

## 답변 스타일
- 첫 인사 후 본론 직행
- 짧고 명확하게
- 여러 항목은 줄바꿈으로 구분
- 상품 추천 시 형식: "선박명 (출발일)\n노선 설명\nhttps://www.cruiselink.co.kr/cruise-view/?ref=REF코드"

## 크루즈 기본 지식
- 객실: 내측(창문없음/저렴) / 외측(고정창/바다뷰) / 발코니(전용발코니/인기) / 스위트(최고급)
- 식사: 메인 다이닝룸 3식 포함, 스페셔티 레스토랑은 별도(약 30~50달러)
- 다이닝: Fixed(시간지정) / My Choice(자유시간)
- 선내 부대시설 대략 금액: 음료패키지 30~60달러/일, 인터넷 15~25달러/일, 스파 100~150달러/50분
- 취소 규정(MSC): 75일전 없음 / 74~60일 $150 / 59~50일 25% / 49~30일 50% / 29~0일 100%
- 기항지 투어: MSC 공식 엑스커션 또는 자유일정
- 선내 결제: Ship Card(신용카드 연결), 현금 가능, USD 기준
- 환전소: 대부분 선박 내 ATM/환전소 운영 (환율 불리할 수 있어 사전 환전 권장)
- 금지물품: 가열기구, 외부주류(선사 정책별 상이), 총기/폭발물, 드론

10. 크루즈 외 질문(회사 내부 정보, 개발/기술 현황, 프로젝트, 직원 정보, AI 시스템 등) → "크루즈 관련 문의만 안내드릴 수 있습니다." 로만 응대
11. 크루즈링크 내부 운영 방식, 백오피스, 개발 현황, 파트너사 등 모든 내부 정보 절대 발설 금지

한국어로만 답변하세요.`;

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { messages, cruiseContext } = req.body;
  if (!messages || !Array.isArray(messages)) return res.status(400).json({ error: 'Invalid messages' });

  const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
  if (!ANTHROPIC_API_KEY) return res.status(500).json({ error: 'API key not configured' });

  // 시스템 프롬프트에 크루즈 컨텍스트 추가
  let systemPrompt = SYSTEM_PROMPT;
  if (cruiseContext && cruiseContext.length > 0) {
    systemPrompt += `\n\n## 현재 추천 가능한 크루즈 상품 (최신 데이터)\n`;
    cruiseContext.slice(0, 20).forEach(c => {
      systemPrompt += `- ${c.shipTitle} | ${c.dateFrom} ${c.nights}박 | ${c.portRoute || c.destination} | ref:${c.ref}\n`;
    });
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5',
        max_tokens: 1024,
        system: systemPrompt,
        messages: messages.slice(-10) // 최근 10개만 전송
      })
    });

    if (!response.ok) {
      const err = await response.text();
      console.error('Anthropic API error:', err);
      return res.status(500).json({ error: 'AI service error' });
    }

    const data = await response.json();
    const reply = data.content?.[0]?.text || '죄송합니다. 잠시 후 다시 시도해 주세요.';
    return res.json({ reply });

  } catch (e) {
    console.error('ai-chat error:', e);
    return res.status(500).json({ error: e.message });
  }
}
