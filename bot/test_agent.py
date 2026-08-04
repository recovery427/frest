"""agent.py 검증. 네트워크도 API 키도 없이 가짜 LLM/클라이언트로 돌린다.

    python3 bot/test_agent.py

채점 루프, 재작성 잠금장치, 자리표시자 차단, 큐 구성을 확인한다.
실제 Threads/Anthropic 호출은 여기서 검증되지 않는다 — 그건 --smoke 몫이다.
"""
import json
import pathlib
import sys
import types
from datetime import datetime, timezone

BOT = pathlib.Path(__file__).resolve().parent

# ── anthropic / threads_api 스텁 ────────────────────────
fake_anthropic = types.ModuleType("anthropic")


class _Anthropic:
    pass


fake_anthropic.Anthropic = _Anthropic
sys.modules["anthropic"] = fake_anthropic

fake_threads = types.ModuleType("threads_api")


class ThreadsError(Exception):
    pass


class ThreadsClient:
    pass


fake_threads.ThreadsError = ThreadsError
fake_threads.ThreadsClient = ThreadsClient
fake_threads.from_env = lambda: None
sys.modules["threads_api"] = fake_threads

sys.path.insert(0, str(BOT))
import agent  # noqa: E402

ok = fail = 0


def check(name, cond):
    global ok, fail
    if cond:
        ok += 1
        print(f"  통과  {name}")
    else:
        fail += 1
        print(f"  실패  {name}")


class Block:
    type = "text"

    def __init__(self, text):
        self.text = text


class Resp:
    def __init__(self, text, stop_reason="end_turn"):
        self.content = [Block(text)]
        self.stop_reason = stop_reason


class FakeLLM:
    """system 프롬프트가 채점표인지 페르소나인지로 채점/재작성을 구분한다."""

    def __init__(self, scores, rewrites):
        self.scores = list(scores)
        self.rewrites = list(rewrites)
        self.messages = self
        self.score_calls = 0
        self.rewrite_calls = 0

    def create(self, **kw):
        is_scoring = "채점 기준" in kw["system"][0]["text"]
        if is_scoring:
            self.score_calls += 1
            return self.scores.pop(0)
        self.rewrite_calls += 1
        return self.rewrites.pop(0)


def verdict(score, fix="첫 줄을 바꿀 것"):
    return Resp(json.dumps({"score": score, "verdict": "pass" if score >= 70 else "rewrite",
                            "weakest": "첫 줄", "fix": fix}, ensure_ascii=False))


print("\n[1] 큐 파일")
queue = json.loads((BOT / "queue.json").read_text(encoding="utf-8"))
check("14개 항목", len(queue) == 14)
check("id 중복 없음", len({i["id"] for i in queue}) == len(queue))
check("모든 항목에 kind", all(i.get("kind") in {"info", "clinic", "sale"} for i in queue))
check("발행 시각 오름차순", [i["publish_at"] for i in queue] == sorted(i["publish_at"] for i in queue))
kinds = [i["kind"] for i in queue]
check(f"상담 글 4건 (실제 {kinds.count('clinic')})", kinds.count("clinic") == 4)
check(f"판매 글 2건 (실제 {kinds.count('sale')})", kinds.count("sale") == 2)
check("자리표시자는 판매글에만",
      all((agent.PLACEHOLDER in i["text"]) == (i["kind"] == "sale") for i in queue))
check("상담 글에 판매/링크 언급 없음",
      all("19,000" not in i["text"] and "원에" not in i["text"]
          for i in queue if i["kind"] == "clinic"))
check("모든 kind가 KIND_LABEL에 있음", all(k in agent.KIND_LABEL for k in kinds))

print("\n[2] 유틸")
check("숫자 추출", agent._numbers("215크레딧 19,000원 84%") == {"215", "19000", "84"})
check("없던 숫자 검출", agent._numbers("7과 45") - agent._numbers("7크레딧") == {"45"})
check("코드펜스 JSON 파싱",
      agent._parse_json('```json\n{"score": 80}\n```\n설명') == {"score": 80})
check("JSON 아님 -> None", agent._parse_json("점수는 80점입니다") is None)
check("깨진 JSON -> None", agent._parse_json('{"score": }') is None)

print("\n[3] polish")
llm = FakeLLM([verdict(74)], [])
check("첫 채점 통과 -> 원문 그대로", agent.polish(llm, "p", "원문", "info") == "원문")
check("  재작성 호출 없음", llm.rewrite_calls == 0)

llm = FakeLLM([verdict(52), verdict(81)], [Resp("고친 글")])
check("한 번 고쳐서 통과", agent.polish(llm, "p", "원문", "info") == "고친 글")

llm = FakeLLM([verdict(40), verdict(50), verdict(60)], [Resp("가 고침"), Resp("나 고침")])
check("두 번 고쳐도 미달 -> 원문", agent.polish(llm, "p", "원문", "info") == "원문")
check("  재작성 정확히 2회", llm.rewrite_calls == 2)

llm = FakeLLM([Resp("채점 못하겠습니다")], [])
check("채점 실패 -> 원문", agent.polish(llm, "p", "원문", "info") == "원문")

llm = FakeLLM([verdict(30)], [Resp("어쩌고 99크레딧")])
check("없던 숫자 지어내면 버림", agent.polish(llm, "p", "원문 7크레딧", "info") == "원문 7크레딧")

llm = FakeLLM([verdict(30)], [Resp("링크 지운 글")])
check("자리표시자 지우면 버림",
      agent.polish(llm, "p", "판매 [링크]", "sale") == "판매 [링크]")

llm = FakeLLM([verdict(30)], [Resp("거부", stop_reason="refusal")])
check("재작성 거부 -> 원문", agent.polish(llm, "p", "원문", "info") == "원문")

llm = FakeLLM([Resp("무시", stop_reason="refusal")], [])
check("채점 거부 -> 원문", agent.polish(llm, "p", "원문", "info") == "원문")

print("\n[4] run_queue")


class FakeClient:
    def __init__(self):
        self.published = []

    def publish_text(self, text, reply_to_id=None):
        self.published.append(text)
        return "media-1"


# 큐 전체가 지난 시점으로 고정한다. 실제 시각에 따라 결과가 달라지면 안 된다.
LATER = datetime(2026, 12, 31, tzinfo=timezone.utc)


def run(state, score_seq=None, rewrite_seq=None, dry=False, score=True):
    c = FakeClient()
    llm = FakeLLM(score_seq or [], rewrite_seq or [])
    n = agent.run_queue(c, llm, "persona", state, dry, score=score, now=LATER)
    return c, n, llm


st = {"published_queue_ids": [], "replied_ids": [], "skipped_ids": []}
c, n, llm = run(st, [verdict(75)])
check("시간이 된 것 1건만 발행", n == 1 and len(c.published) == 1)
check("  d0-cap이 나감", st["published_queue_ids"] == ["d0-cap"])
check("  채점 1회", llm.score_calls == 1)

c, n, llm = run(st, [verdict(75)])
check("이미 발행한 건 건너뜀", st["published_queue_ids"] == ["d0-cap", "d1-clinic-symptom"])

# 판매글까지 전부 밀어본다 — [링크]에서 멈춰야 한다
st2 = {"published_queue_ids": [i["id"] for i in queue if i["id"] != "d7-sale"],
       "replied_ids": [], "skipped_ids": []}
c, n, llm = run(st2, [verdict(90)])
check("[링크] 남은 판매글은 발행 안 됨", n == 0 and c.published == [])
check("  상태에도 안 남음", "d7-sale" not in st2["published_queue_ids"])
check("  채점도 안 함 (호출 0회)", llm.score_calls == 0)

st3 = {"published_queue_ids": [], "replied_ids": [], "skipped_ids": []}
c, n, llm = run(st3, [], score=False)
check("--no-score면 채점 안 함", llm.score_calls == 0 and n == 1)

st4 = {"published_queue_ids": [], "replied_ids": [], "skipped_ids": []}
c, n, llm = run(st4, [verdict(90)], dry=True)
check("dry-run은 발행 안 함", n == 0 and c.published == [] and st4["published_queue_ids"] == [])
check("  dry-run도 채점은 함", llm.score_calls == 1)

print(f"\n통과 {ok} / 실패 {fail}")
sys.exit(1 if fail else 0)
