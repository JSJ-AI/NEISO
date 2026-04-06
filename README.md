# NEISO Grid Monitor

Cloudflare Worker proxy + dashboard for ISO-NE Web Services API.

## Worker Deploy

```bash
wrangler secret put ISONE_USER   # jeff@j2analytics.ai
wrangler secret put ISONE_PASS   # your ISO-NE password
wrangler deploy
```

## Proxied Endpoints

| Data | Worker path |
|------|------------|
| LMPs all zones | /proxy/fiveminutelmp/current/locationType/LOAD ZONE |
| System load | /proxy/fiveminutesystemload/current |
| External flows | /proxy/fiveminuteexternalflow/current |
| Zonal load | /proxy/fiveminuteestimatedzonalload/current |
| Fuel mix | /proxy/genfuelmix/current |
| RT constraints | /proxy/realtimeconstraints/current |

## Security
Credentials stored as Cloudflare encrypted secrets only — never in code.
**Change ISO-NE password after first deploy**, then: `wrangler secret put ISONE_PASS`
