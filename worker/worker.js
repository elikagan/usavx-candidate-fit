// USAVX notes backend — shared notes via Cloudflare KV.
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
        const raw = await env.NOTES.get("all");
        return json(raw ? JSON.parse(raw) : {});
      }
      if (req.method === "POST") {
        const { id, text } = await req.json();
        if (!id) return json({ error: "missing id" }, 400);
        const raw = await env.NOTES.get("all");
        const all = raw ? JSON.parse(raw) : {};
        if (text && text.trim()) all[id] = { text, updated: Date.now() };
        else delete all[id];
        await env.NOTES.put("all", JSON.stringify(all));
        return json({ ok: true });
      }
      return json({ error: "method not allowed" }, 405);
    } catch (e) {
      return json({ error: String(e) }, 500);
    }
  },
};
