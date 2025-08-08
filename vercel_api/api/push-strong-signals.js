export const config = { runtime: 'nodejs' };

async function fetchWithTimeout(url, opts = {}, ms = 15000) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), ms);
  try { return await fetch(url, { ...opts, signal: c.signal }); }
  finally { clearTimeout(t); }
}

export default async function handler(req, res) {
  try {
    let worker = process.env.WORKER_URL;
    if (!worker) return res.status(500).json({ error: 'WORKER_URL not set' });
    if (!/^https?:\/\//i.test(worker)) worker = 'https://' + worker;

    await fetchWithTimeout(`${worker}/health`).catch(() => {});
    const r = await fetchWithTimeout(`${worker}/check-strong-signals`, { method: 'POST' }, 15000);
    const text = await r.text();
    try {
      const data = JSON.parse(text);
      return res.status(200).json(data);
    } catch {
      return res.status(502).json({ error: 'Worker non-JSON', status: r.status, body: text });
    }
  } catch (e) {
    return res.status(500).json({ error: String(e) });
  }
}
