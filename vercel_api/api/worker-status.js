export const config = { runtime: 'nodejs' };

export default async function handler(req, res) {
  try {
    let worker = process.env.WORKER_URL;
    if (!worker) return res.status(500).json({ ok:false, error: 'WORKER_URL not set' });
    if (!/^https?:\/\//i.test(worker)) worker = 'https://' + worker;

    const r = await fetch(worker + '/health', { cache: 'no-store' });
    const text = await r.text();
    const ok = r.ok && /"ok":\s*true/.test(text);
    return res.status(ok ? 200 : 502).json({ ok, status: r.status, body: text });
  } catch (e) {
    return res.status(500).json({ ok:false, error: String(e) });
  }
}
