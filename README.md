# safelink-solver

Resolves SafelinkU / `sfl.gl` ad-links to their final destination over plain HTTP.
No browser, no JavaScript execution, no timers.

## Implementations

| File | Runtime | Lines | Chars | Time* |
|---|---|---|---|---|
| `solver.pl` | Perl 5.14+ (core modules only) | 9 | 786 | ~3.4s |
| `solver.mjs` | Bun | 12 | 824 | ~0.8-2.7s |
| `solver.php` | PHP 8 + curl | 13 | 922 | ~2.6-3.9s |
| `solver.py` | Python 3 + `requests` | 38 | 1334 | ~1.7s |

\* same link, same machine. Timing on this host varies with Cloudflare edge
latency; the ordering is stable.

Pick by what you care about: Perl is the shortest to read, Bun is the fastest,
Python is the most portable. PHP and Perl trade speed for brevity.

## Usage

```bash
perl solver.pl  https://sfl.gl/cgcpp
bun  solver.mjs https://sfl.gl/cgcpp
php  solver.php https://sfl.gl/cgcpp
python solver.py https://sfl.gl/cgcpp
```

Each prints the destination URL.

## How it works

| Step | Request | Purpose |
|------|---------|---------|
| 1 | `GET sfl.gl/<alias>` | Page carries `ray_id` + `alias` in a hidden form |
| 2 | `GET app.khaddavi.net/redirect.php?ray_id&alias` | Sets `__session` |
| 3 | `GET <302 target>` | Sets `XSRF-TOKEN`, `SESSION`, `tt` |
| 4 | `POST /api/verify` | `{"_a": 0}` with `content-type: application/json` |
| 5 | `POST /api/go` | Returns the `sfl.gl/ready/go` ticket |
| 6 | `GET <ticket>` | Destination is in a `window.location.href` string |

### What turned out to be optional

- `/api/session` and the 10s + 3s waits the front-end uses.
- `Referer`, `Origin`, `X-Requested-With`.
- The `X-XSRF-TOKEN` header itself. The cookie alone is accepted.
- URL-decoding the `XSRF-TOKEN` cookie.

### What is mandatory

- `ray_id` must be the real one from step 1. A fabricated value returns
  `{"message":"Page expired"}`.
- Step 3 cannot be skipped: it is the only response that issues `XSRF-TOKEN`.
- `/api/verify` must run before `/api/go`, and the POST body must be sent with
  `content-type: application/json`, or the server returns HTML.

## PHP setup note

Windows builds ship without a CA bundle, so curl fails with
`unable to get local issuer certificate`. Download `cacert.pem` from
<https://curl.se/ca/cacert.pem> and point `curl.cainfo` at it in `php.ini`,
and enable `extension=curl`.

## Notes

- Link-specific: `app.khaddavi.net` is the ad host for this SafelinkU instance.
- Gated links (passcode / Turnstile) return no `url` and the script fails loudly.
- `curl` on Windows builds linked against schannel cannot reach the shortener
  at all (`http_code=000`). Bun, Python and PHP-curl use OpenSSL-family stacks
  and work.

## License

GPL-3.0 — see [LICENSE](LICENSE).
