# AI 광고영상이 어색한 진짜 이유

프롬프트 원문과 실패 로그 전부

---

## 들어가며 — 이 책이 안 다루는 것

Higgsfield 가입법, 크레딧 충전법, 버튼 위치. 이런 건 안 씁니다. 블로그에 무료로 널려 있고, 그걸 몰라서 막힌 사람은 없습니다.

막히는 지점은 다릅니다. 툴은 다 배웠는데 결과물이 안 팔리게 나옵니다. 손가락이 여섯 개고, 얼굴이 컷마다 바뀌고, 제품 로고가 뭉개지고, 뭔가 전체적으로 "AI 같습니다". 그런데 뭘 고쳐야 하는지는 아무도 안 알려줍니다.

이 책은 그 지점만 다룹니다.

K-뷰티 광고 숏폼 한 편을 처음부터 끝까지 실제로 만들면서 나온 것들입니다. **프롬프트 원문 전체, 실측 크레딧 단가, 그리고 실제로 깨진 결과물과 그걸 고친 정확한 문장.** 성공 사례만 모은 자료가 아니라 실패 로그가 절반입니다.

읽고 나면 프롬프트를 복붙해서 바로 돌릴 수 있고, 결과가 깨졌을 때 어디를 만져야 하는지 압니다.

---

# 1장 · 당신의 AI 영상이 어색한 6가지 이유

## 1-1. 지시하지 않은 동작은 일어나지 않는다

가장 많이 하는 착각입니다. 생성 모델이 상식적으로 알아서 채워줄 거라고 기대합니다. 안 채웁니다.

실제로 있었던 일입니다. 립 틴트 광고를 만들면서 이렇게 썼습니다.

> "모델이 립 틴트를 입술에 바르고, 입술을 다문다"

결과물에서 모델은 **뚜껑을 열지 않은 채로** 틴트를 입술에 문질렀습니다. 물리적으로 불가능한 장면인데 모델은 아무 문제를 못 느낍니다. "바른다"는 지시를 받았고, "뚜껑을 연다"는 지시는 못 받았으니까요.

고친 문장은 이렇습니다.

> "모델이 다른 손으로 뚜껑을 돌려 빼고 화면 밖으로 내린다. 그러면 끝에 틴트가 묻은 어플리케이터가 드러난다. 그 다음에 어플리케이터를 입술로 가져가 바른다. **뚜껑을 여는 동작이 반드시 먼저 보여야 하고, 닫힌 상태의 튜브가 입술에 닿아서는 안 된다.**"

핵심은 두 가지입니다. **순서를 명시**하고, **금지 동작을 못 박습니다.** 하지 말아야 할 것을 안 쓰면 모델은 그걸 할 수 있는 선택지로 남겨둡니다.

이 원칙은 모든 제품에 적용됩니다.

| 제품 | 빼먹기 쉬운 동작 |
|---|---|
| 파운데이션·쿠션 | 퍼프를 꺼낸다 / 뚜껑을 연다 |
| 스킨케어 펌프 | 펌프를 누른다 / 손바닥에 덜어낸다 |
| 마스카라 | 브러시를 빼낸다 / 여분을 훑는다 |
| 향수 | 캡을 벗긴다 |
| 음료 | 뚜껑을 돌려 딴다 |

## 1-2. 제품이 프레임에서 사라진다

앞의 영상을 고친 뒤 두 번째 문제가 나왔습니다. 뚜껑은 제대로 열렸는데, 그 순간부터 **유리 튜브 본체가 화면에서 사라졌습니다.** 손에 얇은 어플리케이터 막대만 남았습니다.

광고에서 제품이 사라지는 건 뚜껑보다 심각합니다. 주인공이 없어진 거니까요.

원인은 이렇습니다. 모델이 "뚜껑을 빼고 어플리케이터로 바른다"는 지시를 받으면 어플리케이터에 주의를 집중하고 튜브를 배경 취급합니다. 5초 안에 여러 동작을 넣을수록 심해집니다.

고칠 문장:

> "뚜껑을 뺀 뒤에도 **튜브 본체는 계속 손에 쥔 상태로 프레임 안에 완전히 보이게 유지한다.** 어플리케이터만 단독으로 보이는 컷은 없다."

일반화하면 이렇습니다. **제품 광고의 모든 영상 프롬프트에는 "제품이 프레임 안에 계속 보인다"는 문장이 들어가야 합니다.** 당연해 보여서 안 쓰는데, 당연한 걸 안 쓰면 사라집니다.

## 1-3. 비포가 없다

립 틴트 영상의 시작 프레임에서 모델의 입술은 **이미 발라져 있었습니다.** 그 상태에서 바르는 동작을 하니 아무 변화가 없습니다. 화장품 광고에서 비포/애프터가 없으면 광고가 아니라 그냥 영상입니다.

시작 이미지를 만들 때 이걸 놓칩니다. "모델이 제품을 들고 있는 컷"을 만들면 모델은 당연히 예쁘게 화장한 상태로 나옵니다. 그게 기본값입니다.

고치려면 시작 이미지 프롬프트에서 명시합니다.

> "입술은 아직 제품을 바르지 않은 상태 — 자연스러운 맨입술 톤, 옅고 건조기 있는 질감"

그리고 영상 프롬프트에서 변화를 지시합니다.

> "바르기 전 옅은 입술에서 시작해, 바른 뒤 선명한 와인 톤으로 바뀐다"

## 1-4. 색이 점점 과포화된다

같은 영상에서 세 번째 문제. 뒤로 갈수록 립 색이 진해져서 마지막엔 거의 검붉게 갔습니다.

영상 모델은 프레임을 이어 만들면서 앞 프레임의 특징을 증폭시키는 경향이 있습니다. "와인 톤 립"이 프레임마다 조금씩 더 와인이 됩니다. 5초짜리에서도 눈에 띕니다.

고칠 문장:

> "립 컬러는 처음부터 끝까지 **동일한 채도**를 유지한다. 진해지거나 어두워지지 않는다."

색뿐 아니라 조명, 대비, 표정 강도 전부 같은 현상이 있습니다. 유지되어야 하는 것은 "유지된다"고 써야 유지됩니다.

## 1-5. 마지막 프레임을 신경 안 쓴다

립 틴트 영상의 마지막 프레임은 **입을 벌린 상태**였습니다. 말하다 만 것처럼 보입니다.

숏폼은 자동 반복 재생됩니다. 마지막 프레임이 어색하면 그게 매 루프마다 첫인상이 됩니다. 5초 영상을 세 번 보면 어색한 순간을 세 번 봅니다.

고칠 문장:

> "마지막 1초는 입을 다물고 정면을 보는 안정된 포즈로 마무리한다. 동작이 끝난 상태에서 정지한다."

## 1-6. 컷마다 얼굴이 다르다

가장 흔하고 가장 치명적입니다. 이미지 3컷을 따로 생성하면 3명의 다른 사람이 나옵니다.

해결은 프롬프트가 아니라 **구조**입니다. 뒤에서 자세히 다룹니다. 한 줄로 요약하면, 모델 이미지를 먼저 한 장 만들고 그것을 **레퍼런스로 넣어서** 나머지를 생성해야 합니다. 텍스트로 "같은 얼굴"이라고 백 번 써도 안 됩니다.

---

# 2장 · 광고 한 편의 실제 원가

추정치가 아니라 실측입니다. Higgsfield 기준입니다.

## 2-1. 생성 단가

| 항목 | 설정 | 크레딧 |
|---|---|---:|
| GPT Image-2 이미지 1장 | 9:16, high, 2k | **7** |
| Seedance 2.0 영상 1클립 | 5초, 1080p, 9:16 | **45** |

**영상이 이미지의 6.4배입니다.** 이 비율이 작업 순서를 결정합니다.

## 2-2. 광고 1편 기준

15초 숏폼 한 편에 들어가는 것:

| 단계 | 수량 | 크레딧 |
|---|---:|---:|
| 제품 누끼 | 1 | 7 |
| 모델 레퍼런스 | 1 | 7 |
| 광고 이미지 (모델/사용컷/제품) | 3 | 21 |
| 영상 클립 (5초 × 4) | 4 | 180 |
| **합계** | | **215** |

이미지가 35, 영상이 180입니다. **크레딧의 84%가 영상에서 나갑니다.**

## 2-3. 여기서 나오는 작업 원칙

**컨셉이 확정되기 전에 영상을 돌리지 않습니다.**

이미지를 열 장 다시 뽑아도 70 크레딧입니다. 영상 두 클립 값도 안 됩니다. 그러니 이미지 단계에서 마음껏 실패하고, 확정된 뒤에 영상으로 넘어갑니다.

실무에서는 이렇게 합니다.

1. 이미지로 컨셉을 잡는다 — 마음에 들 때까지 반복
2. 클라이언트가 있으면 **이미지 단계에서 컨펌을 받는다**
3. 확정된 이미지를 시작 프레임으로 영상을 만든다

2번을 건너뛰면 영상까지 다 만들고 나서 "톤이 다른데요" 소리를 듣습니다. 그때 다시 만들면 180 크레딧이 날아갑니다.

## 2-4. 실패 비용은 싸다

이 표를 외워두면 판단이 빨라집니다.

| 재생성 | 크레딧 |
|---|---:|
| 이미지 1장 | 7 |
| 영상 1클립 | 45 |

결과물이 애매할 때 고민하는 시간이 크레딧보다 비쌉니다. **애매하면 다시 뽑습니다.** 이게 AI 제작의 실질적인 이점입니다. 촬영은 다시 못 합니다.

---

# 3장 · 파이프라인

순서가 곧 품질입니다. 이 순서를 바꾸면 얼굴이 흔들리고 제품이 변형됩니다.

```
제품 이미지 확보
      ↓
제품 색감 추출  ←── 여기서 전체 톤이 결정된다
      ↓
모델 레퍼런스 1장 생성
      ↓
광고 이미지 3컷 생성  ←── 앞의 두 장을 레퍼런스로 넣는다
      ↓
[컨펌]
      ↓
영상 4클립 생성  ←── 이미지를 시작 프레임으로
      ↓
편집 · 자막 · 음악
```

## 3-1. 제품 색감 추출 — 대부분이 건너뛰는 단계

AI 광고가 "AI 같아 보이는" 큰 이유 하나가 **배경색이 제품과 따로 논다**는 겁니다. 핑크가 아닌 제품인데 배경이 핑크입니다. 프롬프트에 습관적으로 "soft pink gradient"를 쓰기 때문입니다.

제대로 하는 방법:

1. 제품 이미지에서 **주 색상**을 읽는다
2. 그 색의 **채도를 10~15% 낮춘다**
3. 그 톤을 크림/아이보리로 떨어지는 그라디언트의 주색으로 쓴다
4. 모델의 메이크업 톤도 여기에 맞춘다

채도를 낮추는 이유는 제품이 배경에 먹히지 않게 하기 위해서입니다. 배경이 제품과 같은 채도면 제품이 안 보입니다.

| 제품 | 추출 톤 | 배경 그라디언트 |
|---|---|---|
| 코랄 립 | 머스크 코랄 | 머스크 코랄 → 크림 |
| 레드 틴트 | 소프트 와인 | 와인 → 크림 |
| 베이지 쿠션 | 웜 베이지 | 웜 베이지 → 아이보리 |
| 그린 앰플 | 세이지 | 세이지 → 아이보리 |

## 3-2. 레퍼런스 체인 — 얼굴이 안 바뀌게 하는 유일한 방법

이게 이 책에서 가장 중요한 한 장입니다.

**틀린 방법**: 이미지 3장을 각각 텍스트 프롬프트로 생성. "같은 20대 한국 여성"이라고 아무리 자세히 써도 3명의 다른 사람이 나옵니다.

**맞는 방법**:

```
1단계 — 모델 이미지 1장을 텍스트로 생성          → 이 결과의 ID를 보관
2단계 — 제품 누끼 1장을 텍스트로 생성            → 이 결과의 ID를 보관

3단계 — 광고 컷 ①: 1단계 ID를 레퍼런스로 넣고 생성
        광고 컷 ②: 1단계 + 2단계 ID를 둘 다 넣고 생성
        광고 컷 ③: 2단계 ID를 레퍼런스로 넣고 생성
```

프롬프트에는 이렇게 씁니다.

> "레퍼런스 인물의 **정확한 얼굴 정체성과 시각적 일관성을 유지**한다 — 같은 얼굴, 같은 헤어, 같은 메이크업 톤. 단, 포즈와 구도는 레퍼런스와 다르게 한다."

마지막 문장이 중요합니다. 이걸 안 쓰면 레퍼런스와 똑같은 포즈만 반복해서, 3컷이 사실상 한 컷이 됩니다.

## 3-3. 영상은 이미지를 시작 프레임으로

영상을 텍스트만으로 만들면 앞에서 맞춰놓은 얼굴과 색이 전부 무너집니다. 반드시 **확정된 이미지를 시작 프레임(start_image)으로 넣습니다.**

그리고 영상 프롬프트에는 이 문장을 넣습니다.

> "정체성, 헤어, 메이크업, 배경은 시작 프레임과 **정확히 동일하게 유지**된다."

영상 프롬프트는 "무엇을 만들까"가 아니라 **"이 정지 이미지가 어떻게 움직일까"**를 씁니다. 이 관점 전환이 안 되면 영상이 시작 프레임과 딴판으로 나옵니다.

---

# 4장 · 프롬프트 원문

복붙해서 쓰는 원문입니다. `[대괄호]`만 바꾸면 됩니다. 영문으로 쓰는 이유는 생성 모델의 학습 데이터 대부분이 영문이라 지시 해상도가 높기 때문입니다.

## 4-1. 제품 누끼

```
Ultra-realistic isolated product cutout photograph of an unbranded
[제품 형태 — 예: slim cylindrical glass lip tint tube] standing upright.
[재질·색상 묘사 — 예: frosted clear glass body with deep wine-toned liquid
visible inside, matte champagne-gold cap].
The packaging is completely blank — absolutely no text, no lettering,
no logo, no brand name, no symbols anywhere on the product.
Pure white seamless background, clean cutout.
Backlight-first studio lighting: large diffused softbox top-back plus a
narrow side strip light drawing a single soft traveling highlight down the
[재질], restrained specular detail, realistic soft contact shadow beneath.
85mm macro, real product photography texture, controlled highlights,
clean blacks. Minimal high-end Korean cosmetic mood, like a real studio
ad shoot, not AI or CGI.
No text, no logo, no watermark.
```

> **주의**: 실제 브랜드 제품이 있으면 이 단계를 건너뛰고 실물 누끼를 씁니다. 가상 제품은 로고를 못 넣기 때문에 밋밋해집니다. 실물이 언제나 낫습니다.

## 4-2. 모델 레퍼런스

```
Ultra-realistic K-beauty editorial portrait of a Korean woman in her
early-to-mid 20s. Smooth natural oval face, refined balanced features,
large clear eyes with subtle aegyo-sal, delicate long lashes, softly
defined natural brows.
Natural Korean beauty skin: luminous, hydrated, real skin texture with
visible pores, no over-retouch, no plastic filter look.
Long dark brown hair with soft waves, wispy strands framing the face.
Calm almost-neutral expression, direct relaxed eye contact.
Makeup harmonized with a [추출 색상] concept.
Background: soft gradient of [추출 색상] at about 70% saturation into
cream, matte studio cyclorama.
Soft diffused premium beauty studio lighting, bright clean radiant skin,
high-key and airy. 85mm, shallow depth of field, real studio photography
feel. Ultra realistic, high detail skin texture, dewy clear skin.
No text, no logo, no watermark.
```

**핵심 어휘 두 개**

- `real skin texture with visible pores` — 이걸 빼면 피부가 플라스틱처럼 나옵니다. AI 티의 1순위 원인입니다
- `no over-retouch, no plastic filter look` — 위와 세트로 씁니다

## 4-3. 광고 컷 ① 모델 단독 (오프닝)

레퍼런스: 모델 이미지

```
Create an ultra-realistic K-beauty editorial portrait, maintaining the
exact facial identity and visual consistency of the reference person —
same face, same hair, same makeup tone.
[제품 특성에 맞는 무드 한 줄].
Natural Korean beauty skin: luminous, hydrated, real skin texture with
visible pores, no over-retouch, no plastic filter.
Almost-neutral atmospheric expression, calm eye contact,
a new pose different from the reference.
Extreme close-up beauty editorial, tight framing on the face.
Background: soft gradient of [추출 색상] at about 70% saturation falling
into cream and nude, subtle and clean, matte studio cyclorama.
Soft diffused premium beauty studio lighting, bright clean radiant skin.
Bright, airy, luxurious, polished color grade.
No text, no logo, no watermark.
```

## 4-4. 광고 컷 ② 제품 사용컷

레퍼런스: 모델 이미지 + 제품 이미지

```
Ultra-realistic K-beauty product usage editorial.
The model from reference image 1 kept fully consistent — same face,
same hair, same makeup.
The [제품] from reference image 2 kept pristine and identical in shape,
[재질 묘사], and completely blank with no text, no lettering, no logo
anywhere.
The model is naturally [사용 동작 — 예: holding the product just below
her chin in a real usage moment], confident natural hand positioning,
fingers relaxed, the product clearly visible and in focus in the frame.
Half-body vertical framing.
Background: soft gradient of [추출 색상] at about 70% saturation into
cream, matte studio cyclorama.
Soft diffused beauty studio lighting, gentle realistic shadows, creamy
controlled highlights, no harsh AI bloom.
85mm look, shallow depth of field, real studio photography feel,
natural reflections on the product.
No text, no logo, no watermark.
```

**`no harsh AI bloom`** — 이 한 마디가 과한 발광을 잡습니다. AI 광고가 붕 떠 보이는 원인 중 하나입니다.

## 4-5. 광고 컷 ③ 제품 단독 (히어로)

레퍼런스: 제품 이미지

```
Ultra-realistic hero product shot.
The [제품] from the reference image kept pristine and identical — same
silhouette, [재질 묘사], finish immaculate, and completely blank with no
text, no lettering, no logo, no symbols anywhere.
Product centered, standing upright and very slightly angled on a clean
minimal surface.
Background: smooth one-tone gradient of [추출 색상] at about 65%
saturation into cream and ivory, seamless matte, high-key luxury.
Backlight-first studio lighting: large diffused softbox top-back, a
narrow side strip light drawing a single soft traveling highlight down
the [재질], subtle restrained highlights not flashy, realistic soft
shadow under the product.
85mm macro, real product photography texture, controlled specular
detail, clean blacks.
Minimal high-end Korean cosmetic brand mood, like a real studio ad
shoot, not AI or CGI.
No text, no logo, no watermark.
```

배경 채도를 컷 ①②의 70%보다 낮은 **65%**로 두는 이유는, 제품만 있는 컷에서는 배경이 조금이라도 세면 제품이 묻히기 때문입니다.

## 4-6. 영상 4클립

전부 해당 이미지를 **시작 프레임**으로 넣습니다.

**클립 1 — 오프닝** (시작 프레임: 컷 ①)
```
The model holds a calm neutral expression, then slowly lifts her gaze to
meet the camera and gives the faintest breath of a smile. Very subtle
head tilt. Her hair moves gently as if from a soft studio fan.
Camera pushes in almost imperceptibly, a slow gentle dolly toward her face.
Identity, hair, makeup and the background stay exactly consistent with
the start frame.
Realistic natural motion, no morphing, no warping of facial features.
The final second settles into a stable closed-mouth pose facing camera.
Audio: quiet room tone only, a soft breath, no music, no speech.
```

**클립 2 — 사용** (시작 프레임: 컷 ②)
```
The model [개봉 동작 — 예: twists off the cap with her other hand and
lowers it out of frame], revealing [드러나는 부분].
She then [사용 동작].
The [개봉 동작] must be clearly visible and must happen before any
application.
The product body stays held in her hand and fully visible in frame
throughout — never only the applicator alone.
Hand motion is calm and precise, five natural fingers throughout.
The product stays pristine, identical in shape, and completely blank with
no text or logo appearing at any point.
[색상] stays at exactly the same saturation from start to finish — it
does not deepen or darken.
Identity, hair, makeup and the background stay exactly consistent with
the start frame.
The final second settles into a stable closed-mouth pose.
Realistic natural motion, no extra fingers, no morphing.
Audio: quiet room tone, no music, no speech.
```

**클립 3 — 결과** (시작 프레임: 컷 ①)
```
Close beauty shot focused on the finished result. The model turns her
head slowly a few degrees, catching the light so [결과 묘사 — 예: the
tinted lips show their soft glossy sheen], then settles and holds a
confident calm gaze at the camera.
Skin stays luminous with real texture.
Identity, hair, makeup and the background stay exactly consistent with
the start frame.
Camera drifts slowly to the side revealing the cheekbone and jawline.
Realistic natural motion, no morphing, no facial distortion.
Audio: quiet room tone only, no music, no speech.
```

**클립 4 — 히어로** (시작 프레임: 컷 ③)
```
Hero product shot. The [제품] rotates very slowly on its axis while a
narrow strip highlight travels down the [재질], revealing [내용물 묘사].
The product stays pristine, identical in silhouette, and completely blank
with no text or logo appearing at any point.
The background stays exactly consistent with the start frame.
Camera performs a slow macro push toward the product, ending tight on
the [강조 부위].
Real studio product cinematography, controlled specular detail,
no CGI look.
Audio: quiet room tone only, no music, no speech.
```

## 4-7. 15초 구성

```
클립 1 (오프닝) → 클립 2 (사용) → 클립 4 (히어로)
```

클립 3은 대안컷으로 남깁니다. A/B 테스트할 때 클립 3을 오프닝으로 바꾼 버전을 만들면 소재가 두 개가 됩니다.

---

# 5장 · 실패 로그

실제로 나온 결함과 그걸 고친 문장입니다. 이 표만 옆에 두고 작업해도 재생성 횟수가 줄어듭니다.

| # | 증상 | 원인 | 넣을 문장 |
|---|---|---|---|
| 1 | 뚜껑을 안 열고 사용 | 개봉 동작 미지시 | `The cap removal must be clearly visible and must happen before any application` |
| 2 | 제품이 프레임에서 사라짐 | 5초에 동작이 많음 | `The product body stays held in her hand and fully visible in frame throughout` |
| 3 | 비포가 없음 | 시작 이미지가 이미 완성 상태 | 시작 이미지에 `not yet applied, natural bare tone` |
| 4 | 색이 점점 진해짐 | 프레임 간 특징 증폭 | `stays at exactly the same saturation from start to finish` |
| 5 | 마지막 프레임이 어색함 | 종료 포즈 미지정 | `The final second settles into a stable closed-mouth pose` |
| 6 | 컷마다 얼굴이 다름 | 레퍼런스 미사용 | 레퍼런스 체인 구조로 전환 (3-2) |
| 7 | 손가락이 여섯 개 | 손 동작 미지정 | `five natural fingers throughout, calm and precise hand motion` |
| 8 | 피부가 플라스틱 같음 | 리터치 억제 어휘 누락 | `real skin texture with visible pores, no over-retouch, no plastic filter` |
| 9 | 화면이 붕 뜨고 발광함 | 블룸 억제 누락 | `no harsh AI bloom, creamy controlled highlights` |
| 10 | 제품에 없던 글자가 생김 | 부정 지시 1회로 부족 | 프롬프트 앞·뒤에 두 번 쓴다 (`completely blank with no text...` + `No text, no logo, no watermark`) |
| 11 | 3컷이 다 같은 포즈 | 레퍼런스를 그대로 복제 | `a new pose different from the reference` |
| 12 | 제품이 배경에 묻힘 | 배경 채도가 높음 | 배경 채도를 65%로 낮춘다 |

## 5-1. 10번을 따로 설명하는 이유

생성 모델은 부정 지시를 자주 무시합니다. "no text"라고 썼는데 글자가 나옵니다.

실무적으로 효과 있는 방법은 **같은 부정 지시를 프롬프트의 다른 위치에 두 번 쓰는 것**입니다. 한 번은 제품을 묘사하는 문장 안에서, 한 번은 프롬프트 마지막 줄에서. 그래도 나오면 재생성합니다. 7 크레딧입니다.

## 5-2. 검수 체크리스트

납품 전에 반드시 눈으로 봅니다. 자동으로 걸러지지 않습니다.

- [ ] 제품에 없던 글자·로고가 생겼는가
- [ ] 컷마다 얼굴이 같은가
- [ ] 컷마다 제품 형태가 같은가 (캡 색, 실루엣)
- [ ] 손가락 개수와 관절이 정상인가
- [ ] 영상에서 제품이 프레임 밖으로 사라지는 구간이 있는가
- [ ] 마지막 프레임이 정지 포즈로 안정되어 있는가
- [ ] 색이 중간에 변하지 않는가

---

# 6장 · 첫 3초 — 훅 자막

영상이 잘 나와도 첫 3초에 볼 이유가 없으면 넘어갑니다. 자막 한 줄이 조회수를 가릅니다.

## 6-1. 원칙

**훅은 미끼가 아니라 약속입니다.** 첫 줄에서 기대하게 해놓고 본문이 못 채우면 다음부터 안 봅니다. 본문이 실제로 지킬 수 있는 것만 겁니다.

그리고 숏폼에서는 질문보다 **결론 먼저**가 잘 먹힙니다. 3초 안에 볼 이유를 심어야 하니까요.

## 6-2. 8가지 패턴

| 패턴 | 구조 | 예시 |
|---|---|---|
| 결과부터 | 결론·실패를 먼저 | "◯◯ 하다가 6개월 날렸어요" |
| 상식 깨기 | 다들 믿는 걸 반대로 | "사실 ◯◯, 안 중요해요" |
| 셀프 질문 | 평소 고민을 콕 | "왜 내 ◯◯만 반응이 없을까" |
| 손해·자극 | 이득보다 손해에 민감 | "이거 모르고 ◯◯ 하면 후회해요" |
| 비교 | A 말고 B / 전후 | "◯◯ 바꾸기 전 vs 후" |
| 타겟 지목 | 만나고 싶은 사람 호출 | "◯◯ 막막한 분만 보세요" |
| 숫자 | 시간·횟수·비용을 구체적으로 | "100번 해보고 남은 건 이거예요" |
| 가치 약속 | 얻을 결과를 그대로 | "◯◯, 이 순서대로만 하면 돼요" |

## 6-3. AI 티 안 나는 문장 규칙

이걸 어기면 사람이 쓴 것처럼 안 읽힙니다.

- **3박자 나열 금지** — "빠르고, 정확하고, 스마트하게" 같은 거
- **미사여구 금지** — "놀라운", "여정", "~의 마법"
- **교과서체 금지** — "~할 수 있습니다"의 반복
- **작은 숫자 자랑 금지** — "꿀팁 7개!"는 역효과
- **구체적으로** — 추상어 대신 숫자·장면. "많은 도전"이 아니라 "6개월 날린 경험"
- **길이는 30자 안팎** — 길면 자릅니다

## 6-4. 3편이면 패턴을 3개 쓴다

같은 영상에 자막만 바꿔서 3편을 만들면 소재 3개가 됩니다. 이때 **패턴을 다르게** 씁니다. 비슷한 훅 3개는 테스트가 안 됩니다.

예를 들어 립 틴트라면:

- 1편: "이 영상, 촬영 안 했습니다" *(상식 깨기)*
- 2편: "촬영은 2주, 이건 하루 걸렸어요" *(비교)*
- 3편: "제품 사진 1장. 그게 다예요" *(숫자)*

반응 좋은 쪽에 예산을 몰아줍니다.

---

# 7장 · 이걸로 돈을 받는다면

만들 줄 알면 팔 수 있습니다. 실제 가격 설계입니다.

## 7-1. 가격

| 패키지 | 구성 | 납기 | 가격 | 크레딧 |
|---|---|---|---:|---:|
| 스타터 | 숏폼 1편 + 이미지 3컷 | 24시간 | 150,000원 | 201 |
| 스탠다드 | 숏폼 3편 + 이미지 6컷 | 48시간 | 290,000원 | 582 |
| 브랜드 | 숏폼 10편 + 이미지 20컷 + 전속 모델 | 5일 | 890,000원 | 1,940 |

크레딧 원가는 판매가의 1% 수준입니다. 마진 방어보다 **건수 확보**가 훨씬 중요합니다.

## 7-2. 깎아달라고 하면

가격을 내리지 말고 **범위를 줄입니다.** 한 번 깎으면 다음에도 깎입니다.

> "예산이 정해져 있으시면 1편 15만원짜리로 먼저 하나만 돌려보셔도 됩니다."

## 7-3. 반드시 견적서에 쓸 것

- 등장 인물은 전부 AI 생성이며 실존 인물이 아님
- **화장품 효능·성분 등 표시광고의 적법성 검토는 포함되지 않으며, 최종 확인 책임은 광고주에게 있음**
- 실존 인물의 얼굴을 사용한 제작은 진행하지 않음
- 수정 횟수 (스타터 1회 / 스탠다드 2회), 컨셉 전면 변경만 1회로 계산

두 번째 항목을 빼먹으면 나중에 책임을 뒤집어씁니다. 화장품법 표시광고 위반은 광고주 책임이지만, 문구를 대신 써줬으면 분쟁이 됩니다.

## 7-4. 절대 하지 말 것

- **실존 인물 얼굴로 제작** — 본인 동의가 있어도 하지 않습니다. 딥페이크 시비에 한 번 걸리면 끝입니다
- **무료 샘플 제작** — 포트폴리오로 대신합니다
- **선금 없이 착수**
- **자신 없는 납기 약속** — 늘려 부르고 지킵니다

---

# 마치며

이 책의 절반은 실패 로그입니다. 그게 핵심입니다.

AI 영상 제작에서 실력 차이는 "좋은 프롬프트를 아는가"가 아니라 **"깨진 결과물을 보고 어디를 고칠지 아는가"**에서 납니다. 프롬프트는 복붙하면 되지만, 12가지 실패 유형을 겪어보는 데는 시간과 크레딧이 듭니다. 그 시간을 줄이려고 쓴 책입니다.

마지막으로 하나. **실물 제품이 있으면 언제나 그게 낫습니다.** 이 책의 예시는 가상 제품으로 만들었는데, 로고와 타이포그래피를 넣을 수 없어서 밋밋합니다. 실제 광고의 화면 절반은 패키지 디자인이 먹습니다. 팔 제품이 있다면 그 실물 누끼로 시작하세요.

---

*본 자료의 프롬프트는 자유롭게 상업적으로 사용하셔도 됩니다. 자료 자체의 재배포·재판매는 하실 수 없습니다.*
