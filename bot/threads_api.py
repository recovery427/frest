"""Threads(Meta) Graph API 최소 클라이언트.

게시·답글·답글조회만 다룬다. 공식 문서 기준으로 작성했고, 이 컨테이너에서는
graph.threads.net에 접근할 수 없어 실호출 검증을 하지 못했다. 최초 1회
`python3 bot/threads_api.py --smoke` 로 반드시 스모크 테스트할 것.

한도(2026-08 기준): 24시간당 게시 250건 / 답글 1,000건, 시간당 호출 250회.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://graph.threads.net/v1.0"


class ThreadsError(RuntimeError):
    pass


class ThreadsClient:
    def __init__(self, access_token: str, user_id: str, timeout: int = 30):
        if not access_token or not user_id:
            raise ThreadsError("THREADS_ACCESS_TOKEN / THREADS_USER_ID 가 필요합니다")
        self.token = access_token
        self.user_id = user_id
        self.timeout = timeout

    # ── 저수준 ─────────────────────────────────────────

    def _call(self, method: str, path: str, params: dict) -> dict:
        params = {**params, "access_token": self.token}
        url = f"{BASE}/{path.lstrip('/')}"
        data = None
        if method == "GET":
            url = f"{url}?{urllib.parse.urlencode(params)}"
        else:
            data = urllib.parse.urlencode(params).encode()

        req = urllib.request.Request(url, data=data, method=method)
        last_err: Exception | None = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors="replace")
                # 4xx는 재시도해도 같은 결과다. 429만 예외.
                if e.code != 429 and 400 <= e.code < 500:
                    raise ThreadsError(f"{method} {path} -> {e.code} {body}") from e
                last_err = ThreadsError(f"{method} {path} -> {e.code} {body}")
            except urllib.error.URLError as e:
                last_err = ThreadsError(f"{method} {path} -> {e}")
            time.sleep(2 ** attempt)
        raise last_err  # type: ignore[misc]

    # ── 게시 ───────────────────────────────────────────

    def publish_text(self, text: str, reply_to_id: str | None = None) -> str:
        """텍스트 게시물 또는 답글을 올리고 media_id를 돌려준다.

        Threads는 2단계다. 컨테이너를 만들고 나서 publish 한다.
        컨테이너 생성 직후 바로 publish 하면 간헐적으로 실패해서 잠깐 쉰다.
        """
        params = {"media_type": "TEXT", "text": text}
        if reply_to_id:
            params["reply_to_id"] = reply_to_id
        container = self._call("POST", f"{self.user_id}/threads", params)
        creation_id = container.get("id")
        if not creation_id:
            raise ThreadsError(f"컨테이너 생성 실패: {container}")

        time.sleep(3)
        published = self._call(
            "POST", f"{self.user_id}/threads_publish", {"creation_id": creation_id}
        )
        media_id = published.get("id")
        if not media_id:
            raise ThreadsError(f"게시 실패: {published}")
        return media_id

    # ── 조회 ───────────────────────────────────────────

    def my_posts(self, limit: int = 25) -> list[dict]:
        res = self._call(
            "GET",
            f"{self.user_id}/threads",
            {"fields": "id,text,timestamp,permalink", "limit": limit},
        )
        return res.get("data", [])

    def replies_to(self, media_id: str, limit: int = 50) -> list[dict]:
        """특정 게시물에 달린 답글. 내가 쓴 답글도 섞여 나오므로 걸러 써야 한다."""
        res = self._call(
            "GET",
            f"{media_id}/replies",
            {
                "fields": "id,text,username,timestamp,replied_to,is_reply_owned_by_me,hide_status",
                "limit": limit,
            },
        )
        return res.get("data", [])

    def me(self) -> dict:
        return self._call("GET", "me", {"fields": "id,username,threads_profile_picture_url"})


def from_env() -> ThreadsClient:
    return ThreadsClient(
        access_token=os.environ.get("THREADS_ACCESS_TOKEN", ""),
        user_id=os.environ.get("THREADS_USER_ID", ""),
    )


if __name__ == "__main__":
    import sys

    if "--smoke" not in sys.argv:
        print("사용법: python3 bot/threads_api.py --smoke")
        raise SystemExit(2)

    client = from_env()
    print("계정:", json.dumps(client.me(), ensure_ascii=False))
    posts = client.my_posts(limit=5)
    print(f"최근 게시물 {len(posts)}건")
    for p in posts:
        print(" -", p.get("id"), (p.get("text") or "")[:40])
    print("\n토큰·권한 정상입니다.")
