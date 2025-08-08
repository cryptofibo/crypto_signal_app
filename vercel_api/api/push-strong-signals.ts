
import { NextRequest } from 'next/server';
import { fetch } from 'undici';

export const config = { runtime: 'edge' };

export default async function handler(req: NextRequest) {
  const worker = process.env.WORKER_URL;
  if (!worker) {
    return new Response(JSON.stringify({ error: 'WORKER_URL not set' }), { status: 500 });
  }
  const r = await fetch(`${worker}/check-strong-signals`, { method: 'POST' });
  const data = await r.json();
  return new Response(JSON.stringify(data), { headers: { 'content-type': 'application/json' } });
}
