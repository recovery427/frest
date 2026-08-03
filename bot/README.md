# 스레드 운영 봇 — 세팅

2주 동안 사람 없이 돌아가는 구조. 대표님이 해야 할 건 아래 세팅 한 번뿐이다.

## 왜 이런 구조인가

Claude Code 세션은 컨테이너가 사라지면 끝난다. 2주를 버틸 수 없다.
그래서 봇은 **GitHub Actions**에서 돈다. 저장소가 살아 있는 한 계속 깨어난다.

```
[즉시 경로]  답글 달림 → Meta 웹훅 → Cloudflare Worker → repository_dispatch
                                                              ↓
[주기 경로]  크론 15분 ─────────────────────────────→ GitHub Actions
                                                              │
                          ┌───────────────────────────────────┤
                          ↓                                   ↓
              예약 큐에서 시간 된 글 발행          내 글의 새 답글 조회
                    (크론만)                              ↓
                                              Claude로 답글 초안 (opus-5)
                                                          ↓
                                                      답글 발행

   상태(답한 ID)는 bot/state.json에 커밋 → 중복 답글 방지
```

### 반응 속도 — 두 경로를 같이 쓴다

**웹훅이 주 경로다.** Meta가 답글이 달리는 순간 쏴주므로 반응이 **초 단위**다.
폴링 호출이 0이라 API 한도도 안 먹는다. 세팅은 6번 항목.

**크론은 안전망이다.** 웹훅은 유실될 수 있다 — Meta가 재시도에 실패하면 이벤트가
그냥 사라지고, 워커가 죽어 있어도 마찬가지다. 15분 크론이 그걸 주워담는다.
예약 게시물 발행도 크론이 맡는다.

웹훅 없이 크론만 쓰면 **최선 15분, 최악 30분**이다 (GitHub 크론은 최소 5분이고
부하 때 지연된다). 웹훅 세팅이 부담스러우면 크론만으로도 돌아가지만,
"1분 안에 답글"은 웹훅 없이는 안 된다.

> 참고로 유튜브 영상에서 1분마다 댓글을 확인하던 건 웹훅이 아니라 **PC를 켜두고
> 상주 프로세스를 돌린 것**이다. `while True: 확인(); 60초 대기`. 간단하지만
> PC가 꺼지면 끝나고, 답글 3개 받으려고 하루 1,440번 폴링한다. 웹훅이 낫다.

---

## 1. Meta 앱 만들기 (20분)

1. [developers.facebook.com](https://developers.facebook.com) → 앱 만들기
2. **Threads API** 유스케이스 추가
3. 권한 4개 요청: `threads_basic`, `threads_content_publish`, `threads_manage_replies`, `threads_read_replies`
4. 본인 계정은 개발 모드에서 바로 쓸 수 있다. 다른 계정까지 하려면 앱 검수가 필요하다
5. **장기 액세스 토큰** 발급 (단기 토큰은 1시간이면 만료된다)
6. 토큰과 함께 나오는 **Threads 사용자 ID** 기록

> 토큰은 60일이면 만료된다. 만료 전에 갱신하지 않으면 봇이 멈춘다.
> `.github/workflows`에 갱신 잡을 추가하거나, 캘린더에 55일 뒤 알림을 걸어둘 것.

## 2. 시크릿 등록

저장소 → Settings → Secrets and variables → Actions → New repository secret

| 이름 | 값 |
|---|---|
| `THREADS_ACCESS_TOKEN` | 1번에서 받은 장기 토큰 |
| `THREADS_USER_ID` | 1번에서 받은 사용자 ID |
| `ANTHROPIC_API_KEY` | console.anthropic.com 에서 발급 |

## 3. 스모크 테스트 — 건너뛰지 말 것

이 컨테이너에서는 `graph.threads.net`에 접근할 수 없어 **실호출 검증을 못 했다.**
엔드포인트는 문서 기준으로 작성했지만, 실제로 도는지는 확인이 안 된 상태다.

로컬에서 한 번 돌려본다.

```bash
export THREADS_ACCESS_TOKEN=...
export THREADS_USER_ID=...
pip install anthropic
python3 bot/threads_api.py --smoke
```

계정명과 최근 게시물이 나오면 통과다. 실패하면 권한이나 토큰 문제다.

이어서 발행 없이 답글 초안만 확인한다.

```bash
export ANTHROPIC_API_KEY=...
python3 bot/agent.py --dry-run
```

말투가 마음에 안 들면 `bot/persona.md`만 고치면 된다. 코드는 안 건드려도 된다.

## 4. 발행 전 필수 확인

- [ ] `bot/queue.json`의 `d4-sale`, `d9-sale2`에 있는 **`[링크]`를 래피드 URL로 교체**
      (안 바꾸면 판매글에 대괄호가 그대로 올라간다)
- [ ] `publish_at` 날짜가 지금보다 미래인지 확인 (과거면 즉시 한꺼번에 올라간다 —
      한 번에 하나씩만 나가게 막아뒀지만 15분마다 연달아 나간다)
- [ ] Actions 탭에서 **workflow_dispatch → dry_run 체크**해서 한 번 돌려본다

## 5. 켜기

`.github/workflows/threads-bot.yml`이 머지되면 자동으로 돈다.
멈추려면 Actions 탭에서 워크플로를 Disable 한다.

여기까지만 해도 15분 주기로 돌아간다. 초 단위 반응이 필요하면 6번으로.

---

## 6. 웹훅 붙이기 (선택 — 초 단위 반응)

`bot/webhook/` 에 Cloudflare Worker가 있다. 20줄짜리 중계기고, 하는 일은
서명 검증과 GitHub 호출뿐이다. 봇 로직은 전부 저장소에 남는다.

Cloudflare Workers 무료 티어(하루 10만 요청)로 충분하다. 비용 0원.

```bash
npm i -g wrangler
cd bot/webhook
wrangler login

# 시크릿 3개
wrangler secret put THREADS_APP_SECRET   # Meta 앱 대시보드 → 기본 설정 → App Secret
wrangler secret put VERIFY_TOKEN         # 아무 랜덤 문자열 (직접 정하고 기억해둘 것)
wrangler secret put GITHUB_TOKEN         # GitHub PAT, repo 스코프

wrangler deploy
# → https://threads-webhook.<계정>.workers.dev 주소가 나온다
```

Meta 앱 대시보드에서 등록한다.

1. Threads API → **웹훅** 메뉴
2. 콜백 URL: 위에서 나온 워커 주소
3. 인증 토큰: `VERIFY_TOKEN`에 넣은 것과 **똑같은 값**
4. 확인 및 저장 → Meta가 GET으로 한 번 찔러서 검증한다. 여기서 실패하면
   토큰이 다르거나 워커 배포가 안 된 것이다
5. 필드 구독: **`replies`**, **`mentions`**

동작 확인: 본인 계정으로 자기 글에 답글을 달아본다. 몇 초 안에 Actions 탭에
`repository_dispatch` 실행이 뜨면 성공이다. `wrangler tail`로 워커 로그도 볼 수 있다.

> 이 워커도 실제 Meta 트래픽으로 검증하지 못했다. 서명 검증 방식(`X-Hub-Signature-256`,
> HMAC-SHA256, 원문 바이트 기준)은 Meta 공통 규격을 따랐지만, Threads 페이로드의
> 필드명(`replies` / `mentions`)은 실물로 확인이 필요하다. 서명이 맞는데 봇이 안 깨어나면
> `wrangler tail` 로그에서 실제 `field` 값을 보고 `worker.js`의 `hasReply` 조건을 고치면 된다.

---

## 안전장치

코드에 걸어둔 제한들.

| 항목 | 값 | 이유 |
|---|---:|---|
| 실행당 최대 답글 | 8건 | 도배 방지 |
| 실행당 최대 게시물 | 1건 | 밀린 큐가 한꺼번에 나가는 것 방지 |
| 답글 최대 길이 | 400자 | 넘으면 발행하지 않고 건너뜀 |
| 중복 방지 | `state.json` | 답한 ID와 건너뛴 ID를 모두 기록 |
| 동시 실행 | `concurrency` 그룹 | 겹쳐 돌면서 같은 답글에 두 번 답하는 것 방지 |

Threads API 자체 한도는 24시간당 게시 250건 / 답글 1,000건이라 위 설정으로는 닿지 않는다.

## 봇이 답하지 않는 것

`persona.md`에 정의돼 있고, 모델이 `SKIP`을 반환하면 발행하지 않는다.

시비·조롱, 타사 비방, 정치·종교, 무료 제작 요청, 실존 인물 얼굴 요청.

## 밝혀둘 것

이 봇은 **대표님 계정으로, 대표님 대신** 글을 씁니다. 대필 자체는 흔한 일이지만
자동 답글은 선이 애매한 구간입니다. `persona.md`에 이렇게 박아뒀습니다.

> AI인지 물어보면 숨기지 않는다. "답글은 AI 도구로 초안을 잡고 제가 확인해서 올려요"
> 정도로 사실대로 답한다. 아니라고 하지 않는다.

이 줄은 지우지 마시길 권합니다. 아니라고 했다가 들키는 게 처음부터 인정하는 것보다
훨씬 비쌉니다. 그리고 자료에 쓴 경험담은 실제로 있었던 일이라, 그 부분은 거짓이 아닙니다.

## 비용

| 항목 | 대략 |
|---|---|
| GitHub Actions | 공개 저장소 무료 / 비공개 월 2,000분 |
| Threads API | 무료 |
| Claude API | 답글 1건당 수 원. 하루 20건이면 하루 백 원 단위 |

`claude-opus-5`를 `effort: low`로 쓴다. 답글은 짧아서 토큰이 거의 안 든다.
