# safelink-solver

Resolves SafelinkU / `sfl.gl` ad-links to their final destination over plain HTTP.
No browser, no JavaScript, no timers.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python solver.py https://sfl.gl/cgcpp
```

Prints the destination. As a library:

```python
from solver import resolve
resolve("https://sfl.gl/cgcpp")   # -> 'https://github.com/...'
```

## How it works

| Step | Request | Purpose |
|------|---------|---------|
| 1 | `GET sfl.gl/<alias>` | Page carries `ray_id` + `alias` in a hidden form |
| 2 | `GET app.khaddavi.net/redirect.php?ray_id&alias` | Sets the session cookies |
| 3 | `POST /api/verify` | Sends `X-XSRF-TOKEN` header, `{"_a": 0}` |
| 4 | `POST /api/go` | Returns the `sfl.gl/ready/go` ticket |
| 5 | `GET <ticket>` | Destination is in a `window.location.href` string |

The front-end also calls `/api/session` and waits 10s + 3s between verify rounds.
Those are cosmetic — the API accepts the raw XSRF header directly, so this tool
skips both. Full resolve is ~4 seconds.

## Notes

- Link-specific: `app.khaddavi.net` is the ad host for this SafelinkU instance.
  Other deployments run the same protocol on different hosts.
- If a link is gated behind a passcode or Turnstile, `/api/go` returns no `url`
  and the script fails loudly.

## License

GPL-3.0 — see [LICENSE](LICENSE).
