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

// New England utility outage feeds (scraped from public outage maps)
const OUTAGE_FEEDS = {
  eversource_ma: 'https://outagemap.eversource.com/resources/data/external/interval_generation_data/report.json',
  eversource_ct: 'https://outagemap.eversource.com/resources/data/external/interval_generation_data/report.json',
  natgrid_ma:    'https://outagemap.nationalgridus.com/resources/data/external/interval_generation_data/report.json',
  unitil:        'https://unitil.com/outage-central/outage-map',
  gmp:           'https://outagemap.greenmountainpower.com/resources/data/external/interval_generation_data/report.json',
};

function toBase64(str) {
  const bytes = new TextEncoder().encode(str);
  let binary = '';
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary);
}

async function fetchOutages() {
  const results = {};
  await Promise.allSettled(
    Object.entries(OUTAGE_FEEDS).map(async ([key, url]) => {
      try {
        const r = await fetch(url, { headers: { 'Accept': 'application/json' }, signal: AbortSignal.timeout(5000) });
        if (r.ok) results[key] = await r.json();
        else results[key] = { error: r.status };
      } catch(e) {
        results[key] = { error: e.message };
      }
    })
  );
  return results;
}

async function fetchAlerts() {
  const states = ['CT','MA','ME','NH','RI','VT'];
  const results = [];
  await Promise.allSettled(
    states.map(async (s) => {
      try {
        const r = await fetch('https://api.weather.gov/alerts/active?area=' + s, {
          headers: { 'User-Agent': 'NEISO-GridMonitor/1.0' },
          signal: AbortSignal.timeout(5000)
        });
        if (r.ok) {
          const d = await r.json();
          d.features.forEach(f => results.push({
            state: s,
            event: f.properties.event,
            severity: f.properties.severity,
            urgency: f.properties.urgency,
            headline: f.properties.headline,
            areas: f.properties.areaDesc,
            start: f.properties.effective,
            end: f.properties.expires,
          }));
        }
      } catch(e) { /* skip */ }
    })
  );
  return results;
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    const url = new URL(request.url);
    const path = url.pathname;
    const firstSeg = path.split('/').filter(Boolean)[0] || '';

    // Weather alerts route
    if (firstSeg === 'alerts') {
      const data = await fetchAlerts();
      return new Response(JSON.stringify({ alerts: data, updated: new Date().toISOString() }), {
        headers: { ...CORS, 'Content-Type': 'application/json', 'Cache-Control': 'max-age=300' }
      });
    }

    // Outages route
    if (firstSeg === 'outages') {
      const data = await fetchOutages();
      return new Response(JSON.stringify({ outages: data, updated: new Date().toISOString() }), {
        headers: { ...CORS, 'Content-Type': 'application/json', 'Cache-Control': 'max-age=300' }
      });
    }

    // ISONE routes
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
