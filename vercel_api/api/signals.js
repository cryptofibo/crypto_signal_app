export const config = { runtime: 'edge' };

export default async function handler(req) {
  const worker = process.env.WORKER_URL;
  if (!worker) {
    return new Response(JSON.stringify({ error: 'WORKER_URL not set' }), { status: 500 });
  }
  try {
    const r = await fetch(`${worker}/signals?limit=150`);
    const data = await r.json();
    return new Response(JSON.stringify({ signals: data }), {
      headers: { 'content-type': 'application/json' },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), { status: 500 });
  }
}
