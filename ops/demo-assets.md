# 데모 포트폴리오 — 자산 목록

아웃리치·판매 페이지에 쓰는 데모. **가상 제품**으로 만들었다.
브랜드명·로고가 없는 와인톤 립 틴트라서 공개해도 남의 상표를 쓰는 문제가 없다.

컨셉: 추출 색감 **딥 와인 → 크림 그라디언트** (채도 65~70%)

---

## 레퍼런스 (2장)

| 용도 | job_id | 링크 |
|---|---|---|
| 제품 누끼 | `98470cad-7b2d-4540-a8f1-96e3ca49047d` | [png](https://d8j0ntlcm91z4.cloudfront.net/user_3FeRCU01dmvawfbUDKnPQzA1cdy/hf_20260803_041811_98470cad-7b2d-4540-a8f1-96e3ca49047d.png) |
| 모델 | `8148d2b5-2862-4811-b530-fdbeab94b78d` | [png](https://d8j0ntlcm91z4.cloudfront.net/user_3FeRCU01dmvawfbUDKnPQzA1cdy/hf_20260803_041815_8148d2b5-2862-4811-b530-fdbeab94b78d.png) |

## 광고 3컷

| 컷 | job_id | 링크 |
|---|---|---|
| ① 모델 단독 (오프닝) | `8d627010-d3d1-42ce-9f61-ed84afbf1ec6` | [png](https://d8j0ntlcm91z4.cloudfront.net/user_3FeRCU01dmvawfbUDKnPQzA1cdy/hf_20260803_042142_8d627010-d3d1-42ce-9f61-ed84afbf1ec6.png) |
| ② 제품 사용컷 | `53f0022b-73f4-4a9a-bdb1-9f724a57de15` | [png](https://d8j0ntlcm91z4.cloudfront.net/user_3FeRCU01dmvawfbUDKnPQzA1cdy/hf_20260803_042147_53f0022b-73f4-4a9a-bdb1-9f724a57de15.png) |
| ③ 제품 고스트샷 | `7c1dcca6-60ba-4ba6-87cd-8038689318e9` | [png](https://d8j0ntlcm91z4.cloudfront.net/user_3FeRCU01dmvawfbUDKnPQzA1cdy/hf_20260803_042151_7c1dcca6-60ba-4ba6-87cd-8038689318e9.png) |

전부 GPT Image-2 / 9:16 / high / 2k (제품 누끼만 1:1).
**소모: 5장 × 7 = 35 크레딧**

---

## 검수 (사람이 해야 함)

생성 환경에서 CDN이 막혀 있어 이미지 내용을 자동 확인할 수 없다. 눈으로 볼 것:

- [ ] 제품에 **글자·로고가 섞여 들어갔는지** — "no text" 지시를 이미지 모델이 무시하는 일이 흔하다. 있으면 재생성
- [ ] 3컷의 **모델 얼굴이 동일한지** — 다르면 레퍼런스 붙여 재생성
- [ ] 3컷의 **제품 형태가 동일한지** — 캡 색, 병 실루엣
- [ ] 손가락 개수·관절 (사용컷에서 가장 자주 깨진다)

한 장 재생성에 7크레딧이다. 애매하면 그냥 다시 뽑는 게 싸다.

## 판매 페이지에 넣기

1. 위 링크에서 3컷 다운로드
2. `site/img/demo-01.png` ~ `demo-03.png`로 저장
3. `site/index.html`의 `.slot` div 3개를 `<img src="img/demo-01.png" alt="데모 광고 컷 — 모델 단독">` 형태로 교체

## 주의

이 데모를 아웃리치에 쓸 때 **실제 브랜드 작업물인 것처럼 말하지 않는다.**
"직접 만든 샘플입니다"라고 하면 충분하고, 거짓말을 하면 첫 계약에서 바로 들킨다.
