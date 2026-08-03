/**
 * Threads 웹훅 → GitHub Actions 릴레이.
 *
 * Meta가 답글이 달리는 순간 이 워커로 POST를 쏜다. 워커는 서명만 검증하고
 * GitHub repository_dispatch를 호출해 봇을 즉시 깨운다. 봇 로직은 전부
 * 저장소에 있고 여기는 20줄짜리 중계기다.
 *
 *   Meta → Cloudflare Worker → repository_dispatch → Actions (즉시 실행)
 *
 * 폴링이 없으니 지연이 초 단위고 API 호출도 안 먹는다.
 * Cloudflare Workers 무료 티어로 충분하다 (하루 10만 요청).
 *
 * 배포:
 *   npm i -g wrangler && wrangler deploy
 * 시크릿:
 *   wrangler secret put THREADS_APP_SECRET
 *   wrangler secret put VERIFY_TOKEN
 *   wrangler secret put GITHUB_TOKEN     # repo 스코프 PAT
 */

const GITHUB_REPO = "recovery427/frest";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // ── 1. 최초 등록 검증 (Meta가 GET으로 한 번 찌른다) ──
    if (request.method === "GET") {
      const mode = url.searchParams.get("hub.mode");
      const token = url.searchParams.get("hub.verify_token");
      const challenge = url.searchParams.get("hub.challenge");
      if (mode === "subscribe" && token === env.VERIFY_TOKEN) {
        return new Response(challenge, { status: 200 });
      }
      return new Response("forbidden", { status: 403 });
    }

    if (request.method !== "POST") {
      return new Response("method not allowed", { status: 405 });
    }

    // ── 2. 서명 검증 ──────────────────────────────────
    // 원문 바이트 그대로 검증해야 한다. JSON.parse 후 재직렬화하면 깨진다.
    const raw = await request.text();
    const signature = request.headers.get("x-hub-signature-256") || "";
    if (!(await verify(raw, signature, env.THREADS_APP_SECRET))) {
      return new Response("bad signature", { status: 401 });
    }

    // ── 3. 답글 이벤트만 골라서 봇을 깨운다 ─────────────
    let payload;
    try {
      payload = JSON.parse(raw);
    } catch {
      return new Response("bad json", { status: 400 });
    }

    const hasReply = (payload.entry || []).some((entry) =>
      (entry.changes || []).some((c) => c.field === "replies" || c.field === "mentions"),
    );

    // 서명이 맞으면 항상 200을 돌려준다. 여기서 에러를 내면 Meta가
    // 재시도를 반복하다 구독을 끊는다.
    if (!hasReply) {
      return new Response("ok (ignored)", { status: 200 });
    }

    try {
      const res = await fetch(
        `https://api.github.com/repos/${GITHUB_REPO}/dispatches`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${env.GITHUB_TOKEN}`,
            Accept: "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "threads-webhook-relay",
          },
          body: JSON.stringify({ event_type: "threads-reply" }),
        },
      );
      if (!res.ok) {
        console.error("dispatch 실패", res.status, await res.text());
      }
    } catch (err) {
      console.error("dispatch 예외", err);
    }

    return new Response("ok", { status: 200 });
  },
};

async function verify(rawBody, header, secret) {
  if (!header.startsWith("sha256=") || !secret) return false;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(rawBody));
  const expected = [...new Uint8Array(mac)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  const got = header.slice("sha256=".length);
  // 타이밍 공격 방지를 위해 길이를 먼저 맞추고 상수 시간 비교
  if (got.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < got.length; i++) diff |= got.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}
