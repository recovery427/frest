#!/usr/bin/env python3
"""스레드 운영 봇.

GitHub Actions에서 주기적으로 깨어나 두 가지를 한다.

1. 예약 큐에 올라온 게시물 중 시간이 된 것을 발행
2. 내 게시물에 달린 새 답글을 찾아 Claude로 답글 초안을 쓰고 발행

상태(이미 답한 답글 ID, 이미 발행한 큐 항목)는 bot/state.json에 남기고
워크플로가 저장소에 커밋한다. 세션이 사라져도 이어진다.

    python3 bot/agent.py            # 게시 + 답글
    python3 bot/agent.py --dry-run  # 아무것도 올리지 않고 초안만 출력
    python3 bot/agent.py --replies-only
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

import anthropic

from threads_api import ThreadsClient, ThreadsError, from_env

ROOT = pathlib.Path(__file__).resolve().parent
PERSONA = ROOT / "persona.md"
QUEUE = ROOT / "queue.json"
STATE = ROOT / "state.json"

MODEL = "claude-opus-5"
# 답글은 짧고 자주 나간다. 깊게 생각할 일이 아니라 effort를 낮춘다.
# thinking은 끄지 않는다 — 끄면 태그가 새거나 도구 호출이 텍스트로 나오는 알려진 실패가 있다.
EFFORT = "low"
MAX_REPLIES_PER_RUN = 8
MAX_REPLY_CHARS = 400


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


def run_queue(client: ThreadsClient, state: dict, dry_run: bool) -> int:
    if not QUEUE.exists():
        return 0
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    published = set(state["published_queue_ids"])
    now = datetime.now(timezone.utc)

    count = 0
    # 한 번에 하나만 올린다. 여러 개가 밀려 있어도 연달아 도배하지 않는다.
    for item in due_items(queue, published, now)[:1]:
        text = item["text"].strip()
        print(f"[게시] {item['id']}: {text[:60]}...")
        if dry_run:
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
    client: ThreadsClient, llm: anthropic.Anthropic, state: dict, dry_run: bool
) -> int:
    persona = PERSONA.read_text(encoding="utf-8")
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
    args = ap.parse_args()

    client = from_env()
    llm = anthropic.Anthropic()
    state = load_state()

    posted = replied = 0
    if not args.replies_only:
        posted = run_queue(client, state, args.dry_run)
    if not args.queue_only:
        replied = run_replies(client, llm, state, args.dry_run)

    if not args.dry_run:
        save_state(state)

    print(f"\n게시 {posted}건, 답글 {replied}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
