const ISONE_BASE = 'https://webservices.iso-ne.com/api/v1.1';

const ALLOWED = [
  'fiveminutelmp',
  'fiveminutesystemload',
  'fiveminuteexternalflow',
  'fiveminuteestimatedzonalload',
  'genfuelmix',
  'realtimeconstraints',
  'hourlylmp',
];

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function toBase64(str) {
  const bytes = new TextEncoder().encode(str);
  let binary = '';
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary);
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    const url = new URL(request.url);
    const path = url.pathname;
    const firstSeg = path.split('/').filter(Boolean)[0] || '';

    if (!ALLOWED.includes(firstSeg)) {
      return new Response(JSON.stringify({ error: 'Not permitted', path, firstSeg }), {
        status: 403,
        headers: { ...CORS, 'Content-Type': 'application/json' }
      });
    }

    const credentials = toBase64(env.ISONE_USER + ':' + env.ISONE_PASS);
    const upstreamUrl = ISONE_BASE + path + '.json';

    try {
      const upstream = await fetch(upstreamUrl, {
        headers: {
          'Authorization': 'Basic ' + credentials,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      const data = await upstream.text();
      return new Response(data, {
        status: upstream.status,
        headers: { ...CORS, 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: 'Upstream failed', detail: err.message }), {
        status: 502,
        headers: { ...CORS, 'Content-Type': 'application/json' }
      });
    }
  }
};