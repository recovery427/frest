#!/usr/bin/env python3
"""스레드 운영 봇.

GitHub Actions에서 주기적으로 깨어나 두 가지를 한다.

1. 예약 큐에 올라온 게시물 중 시간이 된 것을 발행 (발행 전 자가채점 → 미달이면 재작성)
2. 내 게시물에 달린 새 답글을 찾아 Claude로 답글 초안을 쓰고 발행

상태(이미 답한 답글 ID, 이미 발행한 큐 항목)는 bot/state.json에 남기고
워크플로가 저장소에 커밋한다. 세션이 사라져도 이어진다.

    python3 bot/agent.py            # 게시 + 답글
    python3 bot/agent.py --dry-run  # 아무것도 올리지 않고 초안만 출력
    python3 bot/agent.py --replies-only
    python3 bot/agent.py --no-score # 자가채점 건너뛰기 (디버그용)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

import anthropic

from threads_api import ThreadsClient, ThreadsError, from_env

ROOT = pathlib.Path(__file__).resolve().parent
PERSONA = ROOT / "persona.md"
SCORING = ROOT / "scoring.md"
QUEUE = ROOT / "queue.json"
STATE = ROOT / "state.json"

MODEL = "claude-opus-5"
# 답글은 짧고 자주 나간다. 깊게 생각할 일이 아니라 effort를 낮춘다.
# thinking은 끄지 않는다 — 끄면 태그가 새거나 도구 호출이 텍스트로 나오는 알려진 실패가 있다.
EFFORT = "low"
MAX_REPLIES_PER_RUN = 8
MAX_REPLY_CHARS = 400

# 자가채점 — scoring.md 기준. 게시물에만 적용한다.
# 답글은 2~3문장이라 "첫 줄 30점" 같은 항목을 만족할 수 없다. 채점하면 전부 탈락한다.
SCORE_CUTOFF = 70
MAX_REWRITES = 2
KIND_LABEL = {"info": "정보 글", "clinic": "상담 글", "sale": "판매 글"}

# 링크를 안 채우고 발행하면 판매글에 대괄호가 그대로 올라간다. 코드에서 막는다.
PLACEHOLDER = "[링크]"


# ── 상태 ───────────────────────────────────────────────

def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"replied_ids": [], "published_queue_ids": [], "skipped_ids": []}


def save_state(state: dict) -> None:
    STATE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


# ── 자가채점 ───────────────────────────────────────────
#
# 라이브 방송에서 확인한 구조를 그대로 옮긴 것이다. 글을 쓰고 바로 올리는 게 아니라,
# 자기 글을 채점표에 넣고 기준 미달이면 다시 쓴다. 사람이 개입하지 않고도
# 글의 하한선이 유지되는 유일한 장치다.
#
#   초안 → 채점(scoring.md) → 70점 미만이면 fix 지시대로 재작성 → 다시 채점
#
# 두 번까지만 고친다. 그래도 미달이면 원문으로 발행한다. 발행을 막지 않는 이유는,
# 채점은 어디까지나 모델의 판단이고 예약 글은 이미 사람이 검토한 텍스트이기 때문이다.

_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _numbers(text: str) -> set[str]:
    """숫자 토큰을 뽑는다. 재작성이 없던 숫자를 지어냈는지 보는 데 쓴다."""
    return {m.group().replace(",", "").rstrip(".") for m in _NUMBER.finditer(text)}


def _parse_json(raw: str) -> dict | None:
    """모델이 코드펜스나 설명을 붙여도 JSON만 건져낸다."""
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None


def score_draft(llm: anthropic.Anthropic, text: str, kind: str) -> dict | None:
    """글을 채점한다. 채점 자체가 실패하면 None."""
    rubric = SCORING.read_text(encoding="utf-8")
    prompt = f"""유형: {KIND_LABEL.get(kind, "정보 글")}

<글>
{text}
</글>

채점표대로 채점하고 JSON만 출력하세요."""

    resp = llm.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=[{"type": "text", "text": rubric, "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": EFFORT},
        messages=[{"role": "user", "content": prompt}],
    )
    if resp.stop_reason == "refusal":
        return None

    verdict = _parse_json("".join(b.text for b in resp.content if b.type == "text"))
    if not verdict or not isinstance(verdict.get("score"), (int, float)):
        return None
    return verdict


def rewrite_post(
    llm: anthropic.Anthropic, persona: str, text: str, verdict: dict, kind: str
) -> str | None:
    """채점 결과의 fix 지시대로 다시 쓴다. 못 믿을 결과면 None."""
    prompt = f"""아래 글이 {verdict['score']}점으로 기준(70점) 미달입니다.

가장 약한 항목: {verdict.get('weakest', '알 수 없음')}
고칠 것: {verdict.get('fix', '전반적으로 다시 쓸 것')}

<글>
{text}
</글>

이 지시대로 다시 쓰세요. 지킬 것:

- 유형은 {KIND_LABEL.get(kind, "정보 글")}입니다
- 원문에 없는 숫자를 새로 만들지 마세요. 원문에 있는 숫자만 씁니다
- 원문의 URL과 대괄호 자리표시자는 글자 그대로 남기세요
- 설명이나 따옴표 없이 실제로 올릴 본문만 쓰세요"""

    resp = llm.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=[{"type": "text", "text": persona, "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": EFFORT},
        messages=[{"role": "user", "content": prompt}],
    )
    if resp.stop_reason == "refusal":
        return None

    new = "".join(b.text for b in resp.content if b.type == "text").strip()
    if not new:
        return None

    invented = _numbers(new) - _numbers(text)
    if invented:
        # 페르소나에 "숫자를 지어내지 않는다"가 있지만 재작성은 특히 위험한 구간이다.
        # 한 번 더 막는다.
        print(f"       (재작성이 없던 숫자를 만듦: {sorted(invented)} — 버림)")
        return None
    if PLACEHOLDER in text and PLACEHOLDER not in new:
        print("       (재작성이 자리표시자를 지움 — 버림)")
        return None
    return new


def polish(llm: anthropic.Anthropic, persona: str, text: str, kind: str) -> str:
    """채점 → 미달이면 재작성. 최종 본문을 돌려준다."""
    current = text
    for attempt in range(MAX_REWRITES + 1):
        verdict = score_draft(llm, current, kind)
        if verdict is None:
            print("       (채점 실패 — 원문 그대로 발행)")
            return current

        score = verdict["score"]
        print(f"       채점 {score}점 · 약한 곳: {verdict.get('weakest', '-')}")
        if score >= SCORE_CUTOFF:
            return current
        if attempt == MAX_REWRITES:
            print(f"       ({MAX_REWRITES}번 고쳐도 미달 — 원문으로 발행)")
            return text

        print(f"       고칠 것: {verdict.get('fix', '-')}")
        new = rewrite_post(llm, persona, current, verdict, kind)
        if new is None:
            return text
        current = new
    return current


# ── 예약 게시 ──────────────────────────────────────────

def due_items(queue: list[dict], published: set[str], now: datetime) -> list[dict]:
    out = []
    for item in queue:
        if item["id"] in published:
            continue
        when = datetime.fromisoformat(item["publish_at"].replace("Z", "+00:00"))
        if when <= now:
            out.append(item)
    return sorted(out, key=lambda i: i["publish_at"])


def run_queue(
    client: ThreadsClient,
    llm: anthropic.Anthropic,
    persona: str,
    state: dict,
    dry_run: bool,
    score: bool = True,
    now: datetime | None = None,
) -> int:
    if not QUEUE.exists():
        return 0
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    published = set(state["published_queue_ids"])
    now = now or datetime.now(timezone.utc)

    count = 0
    # 한 번에 하나만 올린다. 여러 개가 밀려 있어도 연달아 도배하지 않는다.
    for item in due_items(queue, published, now)[:1]:
        text = item["text"].strip()
        print(f"[게시] {item['id']}: {text[:60]}...")

        if PLACEHOLDER in text:
            # 발행하지 않고 상태도 남기지 않는다. 링크를 채우면 다음 실행에 나간다.
            print(f"       [보류] {PLACEHOLDER} 자리표시자가 남아 있다. 링크를 채운 뒤 발행된다")
            continue

        if score:
            text = polish(llm, persona, text, item.get("kind", "info"))

        if dry_run:
            print(f"       (dry-run) 최종 본문:\n{text}\n")
            continue
        media_id = client.publish_text(text)
        print(f"       -> {media_id}")
        state["published_queue_ids"].append(item["id"])
        count += 1
    return count


# ── 답글 ───────────────────────────────────────────────

def is_actionable(reply: dict, state: dict) -> bool:
    if reply.get("is_reply_owned_by_me"):
        return False
    if reply["id"] in state["replied_ids"] or reply["id"] in state["skipped_ids"]:
        return False
    if not (reply.get("text") or "").strip():
        return False
    return True


def draft_reply(llm: anthropic.Anthropic, persona: str, post_text: str, reply: dict) -> str | None:
    """답글 초안을 만든다. 답하지 않는 게 맞으면 None."""
    prompt = f"""아래는 내가 올린 스레드 게시물과, 거기 달린 다른 사람의 답글입니다.

<내 게시물>
{post_text}
</내 게시물>

<받은 답글 작성자="{reply.get('username', '알수없음')}">
{reply['text']}
</받은 답글>

이 답글에 뭐라고 답할지 쓰세요.
페르소나의 '답하지 않을 것'에 해당하면 답글 대신 SKIP 이라고만 쓰세요.
설명이나 따옴표 없이 실제로 올릴 문장만 쓰세요."""

    resp = llm.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=[{"type": "text", "text": persona, "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": EFFORT},
        messages=[{"role": "user", "content": prompt}],
    )

    if resp.stop_reason == "refusal":
        print("       (모델이 응답을 거부함 — 건너뜀)")
        return None

    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    if not text or text.upper().startswith("SKIP"):
        return None
    if len(text) > MAX_REPLY_CHARS:
        print(f"       (초안이 {len(text)}자로 너무 김 — 건너뜀)")
        return None
    return text


def run_replies(
    client: ThreadsClient,
    llm: anthropic.Anthropic,
    persona: str,
    state: dict,
    dry_run: bool,
) -> int:
    posts = client.my_posts(limit=15)
    sent = 0

    for post in posts:
        if sent >= MAX_REPLIES_PER_RUN:
            break
        try:
            replies = client.replies_to(post["id"])
        except ThreadsError as e:
            print(f"[경고] {post['id']} 답글 조회 실패: {e}")
            continue

        for reply in replies:
            if sent >= MAX_REPLIES_PER_RUN:
                break
            if not is_actionable(reply, state):
                continue

            print(f"[답글] @{reply.get('username')}: {reply['text'][:60]}")
            draft = draft_reply(llm, persona, post.get("text") or "", reply)
            if draft is None:
                print("       -> SKIP")
                if not dry_run:
                    state["skipped_ids"].append(reply["id"])
                continue

            print(f"       -> {draft}")
            if dry_run:
                continue
            try:
                client.publish_text(draft, reply_to_id=reply["id"])
            except ThreadsError as e:
                print(f"       [실패] {e}")
                continue
            state["replied_ids"].append(reply["id"])
            sent += 1

    return sent


# ── 진입점 ─────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="발행하지 않고 초안만 출력")
    ap.add_argument("--replies-only", action="store_true")
    ap.add_argument("--queue-only", action="store_true")
    ap.add_argument("--no-score", action="store_true", help="게시 전 자가채점을 건너뛴다")
    args = ap.parse_args()

    client = from_env()
    llm = anthropic.Anthropic()
    persona = PERSONA.read_text(encoding="utf-8")
    state = load_state()

    posted = replied = 0
    if not args.replies_only:
        posted = run_queue(client, llm, persona, state, args.dry_run, score=not args.no_score)
    if not args.queue_only:
        replied = run_replies(client, llm, persona, state, args.dry_run)

    if not args.dry_run:
        save_state(state)

    print(f"\n게시 {posted}건, 답글 {replied}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
