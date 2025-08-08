export const config = { runtime: 'edge' };
export default async function handler() {
  const worker = process.env.WORKER_URL;
  if (!worker) return new Response(JSON.stringify({ error: 'WORKER_URL not set' }), { status: 500 });
  const r = await fetch(`${worker}/signals?limit=150`);
  const data = await r.json();
  return new Response(JSON.stringify({ signals: data }), { headers: { 'content-type': 'application/json' } });
}
