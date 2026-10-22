# safelink-solver

Resolves SafelinkU / `sfl.gl` ad-links to their final destination over plain HTTP.
No browser, no JavaScript execution, no timers.

Two implementations, same protocol. Pick one:

| File | Runtime | Lines | Time* |
|---|---|---|---|
| `solver.mjs` | Bun (or Node 20+) | 20 | ~1.0s |
| `solver.py` | Python 3 + `requests` | 38 | ~1.7s |

\* measured on the same link, same machine. Node 24 runs `solver.mjs` correctly
but is ~5x slower (~8.5s) because of per-hop connection setup.

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
| 4 | `POST /api/verify` | Sends `X-XSRF-TOKEN` header, `{"_a": 0}` |
| 5 | `POST /api/go` | Returns the `sfl.gl/ready/go` ticket |
| 6 | `GET <ticket>` | Destination is in a `window.location.href` string |

Two things worth knowing:

- The front-end calls `/api/session` and waits 10s + 3s between verify rounds.
  Both are cosmetic. The API accepts the raw XSRF header directly.
- The `XSRF-TOKEN` cookie is only issued on hop 3, not on hop 2. Losing it
  produces `{"message":"Page expired"}`, which is why the JS version carries a
  tiny cookie jar across hops by hand.

## Notes

- Link-specific: `app.khaddavi.net` is the ad host for this SafelinkU instance.
  Other deployments run the same protocol on different hosts.
- If a link is gated behind a passcode or Turnstile, `/api/go` returns no `url`
  and the script fails loudly.
- `curl` is not usable on Windows builds that link against schannel — the TLS
  handshake to the shortener fails with `http_code=000`.

## License

GPL-3.0 — see [LICENSE](LICENSE).
