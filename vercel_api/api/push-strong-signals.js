export const config = { runtime: 'nodejs18.x' };

export default async function handler(req, res) {
  try {
    const worker = process.env.WORKER_URL;
    if (!worker) return res.status(500).json({ error: 'WORKER_URL not set' });

    const r = await fetch(`${worker}/check-strong-signals`, { method: 'POST' });
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
