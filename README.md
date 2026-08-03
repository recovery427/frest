# frest — 72시간 100만원 작전

AI 광고영상 제작을 상품으로 팔아서 **72시간 안에 매출 100만원**을 만드는 실행 키트.

---

## 먼저, 이 저장소의 전제

Claude(AI)는 혼자 돈을 못 번다. 계좌도 없고, 계약도 못 맺고, 세션이 끝나면 사라진다.
그래서 이 저장소는 **"AI가 돈을 벌어온 결과"가 아니라 "사람이 72시간 안에 100만원을 벌 수 있게 만든 도구 일체"**다.

역할 분담은 이렇게 나눈다.

| | Claude | 사람(대표) |
|---|---|---|
| 상품 설계·가격 | ✅ | 승인 |
| 판매 페이지·포트폴리오 | ✅ | 승인 |
| 아웃리치 문구 작성 | ✅ | — |
| **DM/메일 실제 발송** | ❌ | ✅ |
| **상담·협상·계약** | ❌ | ✅ |
| **입금 받기** | ❌ | ✅ |
| 수주 후 영상 제작 | ✅ | 컨펌 |
| 납품·CS | 초안 | ✅ |

병목은 제작이 아니라 **판매**다. 제작은 Higgsfield Ultra 크레딧 7,199로 이미 해결돼 있다.

---

## 파는 것

**K-뷰티/이커머스 브랜드용 AI 광고영상.** 모델 섭외·스튜디오·촬영 없이, 제품 누끼 1장 + 레퍼런스만 받아서 24~48시간 안에 세로 숏폼 광고를 뽑아준다.

- 실사 촬영 견적 300~800만원 → **15~89만원**
- 촬영 일정 2~3주 → **24~48시간**
- 원가는 Higgsfield 크레딧뿐 (구독료는 이미 매몰비용)

상세: [`sales/offer.md`](sales/offer.md)

---

## 100만원까지의 계산

추천안(B): **스탠다드 29만원 × 4건 = 116만원**

여기 도달하려면 역산해서 이만큼 필요하다.

```
계약 4건  ←  상담/견적 13건  ←  답장 26건  ←  아웃리치 260건
        30%             50%            10%
```

**72시간 안에 260건 접촉**이 이 작전의 전부다. 나머지는 다 준비물이다.
상세: [`plan/unit-economics.md`](plan/unit-economics.md)

---

## 문서

| 파일 | 내용 |
|---|---|
| [`bot/README.md`](bot/README.md) | **스레드 자동 운영 봇 세팅** — 2주간 사람 없이 도는 구조 |
| [`product/manuscript.md`](product/manuscript.md) | 전자책 원고 (판매 상품) |
| [`product/latpeed-listing.md`](product/latpeed-listing.md) | 래피드 상품 등록 문구 |
| [`plan/72h-plan.md`](plan/72h-plan.md) | 시간대별 실행 체크리스트 (H+0 ~ H+72) |
| [`plan/unit-economics.md`](plan/unit-economics.md) | 가격·원가·퍼널 계산, 100만원 도달 시나리오 3안 |
| [`sales/offer.md`](sales/offer.md) | 패키지 3종 정의, 포함/불포함, 납기, 수정 규정 |
| [`sales/outreach.md`](sales/outreach.md) | 인스타 DM·이메일·크몽 소개글·오픈카톡 문구 (복붙용) |
| [`sales/objections.md`](sales/objections.md) | 자주 나오는 반론 12개와 대응 |
| [`sales/quote-template.md`](sales/quote-template.md) | 견적서 양식, 결제·환불·저작권 조항 |
| [`ops/runbook.md`](ops/runbook.md) | 수주 후 제작 SOP — 접수부터 납품까지 |
| [`site/index.html`](site/index.html) | 판매 페이지. DM에 링크로 붙이는 용도 |
| [`tracker.csv`](tracker.csv) | 아웃리치 추적 시트 |

---

## 지금 당장 할 것 (읽자마자 30분 안에)

1. `sales/offer.md` 가격 3줄 확인하고 마음에 안 들면 고친다
2. 데모 포트폴리오 3컷 생성 승인 (Claude에게 "데모 뽑아줘")
3. 판매 페이지 링크 확보
4. `sales/outreach.md` A-1 문구 복사 → 인스타 DM 20건 발송

포트폴리오 없이 아웃리치하면 답장률이 0에 수렴한다. 2번을 건너뛰지 말 것.
