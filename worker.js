/**
 * ISO-NE Web Services Proxy Worker
 * Proxies requests to webservices.iso-ne.com with Basic Auth
 * Deploy to Cloudflare Workers - set ISONE_USER and ISONE_PASS as secrets
 */

const ISONE_BASE = 'https://webservices.iso-ne.com/api/v1.1';

const ALLOWED_PATHS = [
  '/fiveminutelmp/current/locationType/LOAD%20ZONE',
  '/fiveminutesystemload/current',
  '/fiveminuteexternalflow/current',
  '/fiveminuteestimatedzonalload/current',
  '/genfuelmix/current',
  '/realtimeconstraints/current',
  '/hourlylmp/rt/prelim/current',
];

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request, env) {

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    if (request.method !== 'GET') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    const url = new URL(request.url);
    const path = url.pathname.replace(/^\/proxy/, '');

    const isAllowed = ALLOWED_PATHS.some(p =>
      path.startsWith(p.replace('%20', ' ')) ||
      path.startsWith(p)
    );

    if (!isAllowed) {
      return new Response(JSON.stringify({ error: 'Path not permitted', path }), {
        status: 403,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    const credentials = btoa(`${env.ISONE_USER}:${env.ISONE_PASS}`);
    const upstreamUrl = `${ISONE_BASE}${path}.json`;

    let upstream;
    try {
      upstream = await fetch(upstreamUrl, {
        headers: {
          'Authorization': `Basic ${credentials}`,
          'Accept': 'application/json',
        },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: 'Upstream fetch failed', detail: err.message }), {
        status: 502,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    if (!upstream.ok) {
      return new Response(JSON.stringify({ error: 'Upstream error', status: upstream.status }), {
        status: upstream.status,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    const data = await upstream.text();

    return new Response(data, {
      status: 200,
      headers: {
        ...CORS_HEADERS,
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store',
      },
    });
  },
};