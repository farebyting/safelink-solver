# safelink-solver

Resolves SafelinkU / `sfl.gl` ad-links to their final destination over plain HTTP.
No browser, no JavaScript execution, no timers.

| File | Runtime | Lines | Time* |
|---|---|---|---|
| `solver.mjs` | Bun (or Node 20+) | 13 | ~1.0s |
| `solver.py` | Python 3 + `requests` | 38 | ~1.7s |

\* same link, same machine. Node 24 runs `solver.mjs` correctly but is ~5x
slower (~8.5s) because of per-hop connection setup.

## Usage

```bash
bun solver.mjs https://sfl.gl/cgcpp
# or
python solver.py https://sfl.gl/cgcpp
```

Prints the destination URL. Python as a library:

```python
from solver import resolve
resolve("https://sfl.gl/cgcpp")   # -> 'https://github.com/...'
```

## How it works

| Step | Request | Purpose |
|------|---------|---------|
| 1 | `GET sfl.gl/<alias>` | Page carries `ray_id` + `alias` in a hidden form |
| 2 | `GET app.khaddavi.net/redirect.php?ray_id&alias` | Sets `__session` |
| 3 | `GET <302 target>` | Sets `XSRF-TOKEN`, `SESSION`, `tt` |
| 4 | `POST /api/verify` | `{"_a": 0}` |
| 5 | `POST /api/go` | Returns the `sfl.gl/ready/go` ticket |
| 6 | `GET <ticket>` | Destination is in a `window.location.href` string |

Things that turned out to be optional:

- `/api/session` and the 10s + 3s waits. The front-end calls them; the API
  doesn't require them.
- `Referer`, `Origin`, `X-Requested-With`. None are checked.
- URL-decoding the `XSRF-TOKEN` cookie before sending it as `X-XSRF-TOKEN`.
  The encoded value is accepted as-is.

Things that are not optional:

- `ray_id` must be the real one from step 1. A fabricated value returns
  `{"message":"Page expired"}`.
- Step 3 is required: it is the only response that issues `XSRF-TOKEN`.
  Dropping it, or skipping `/api/verify`, also yields `Page expired`.

## Notes

- Link-specific: `app.khaddavi.net` is the ad host for this SafelinkU instance.
  Other deployments run the same protocol on different hosts.
- Gated links (passcode / Turnstile) return no `url` from `/api/go` and the
  script fails loudly.
- `curl` on Windows builds linked against schannel cannot reach the shortener
  at all — TLS handshake fails with `http_code=000`. Python and Bun use
  OpenSSL/BoringSSL, so they work.

## License

GPL-3.0 — see [LICENSE](LICENSE).
