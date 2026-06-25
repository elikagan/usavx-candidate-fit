// USAVX shared notes — Cloudflare D1 (strongly consistent SQLite).
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};
export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
    const json = (o, s = 200) =>
      new Response(JSON.stringify(o), { status: s, headers: { ...CORS, "Content-Type": "application/json" } });
    try {
      if (req.method === "GET") {
        const { results } = await env.DB.prepare("SELECT id, text, updated FROM notes").all();
        const out = {};
        for (const r of results) out[r.id] = { text: r.text, updated: r.updated };
        return json(out);
      }
      if (req.method === "POST") {
        const { id, text } = await req.json();
        if (!id) return json({ error: "missing id" }, 400);
        if (text && text.trim()) {
          await env.DB.prepare(
            "INSERT INTO notes (id, text, updated) VALUES (?, ?, ?) " +
            "ON CONFLICT(id) DO UPDATE SET text=excluded.text, updated=excluded.updated"
          ).bind(id, text, Date.now()).run();
        } else {
          await env.DB.prepare("DELETE FROM notes WHERE id = ?").bind(id).run();
        }
        return json({ ok: true });
      }
      return json({ error: "method not allowed" }, 405);
    } catch (e) {
      return json({ error: String(e) }, 500);
    }
  },
};
