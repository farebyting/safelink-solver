# safelink-solver

Resolves SafelinkU / `sfl.gl` ad-links to their final destination over plain HTTP.
No browser, no headless Chrome, no JS execution.

## Why

Ad-link gateways like SafelinkU serve a chain of decoy pages and require a
cookie handshake plus two timed "verify" rounds before they hand over a signed
ticket to the destination. Browsers do this invisibly through JavaScript. This
script replays the exact same protocol with `requests`.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python solver.py https://sfl.gl/cgcpp
```

Output is the resolved URL on stdout, progress on stderr:

```
[1] ray_id:  EccmKrFg07vZFVMeoKpZvlKfa6IS15tF  alias:  cgcpp
[2] landed:  https://app.khaddavi.net/aplikasi-game-puzzle-.../
[3.0] session:  {'step': 1, 'fb': False, 'captcha': None, 'passcode': False}
[3.0] waiting 10s
[3.0] verify:  {'message': 'OK', 'target': '...'}
[3.1] session:  {'step': 2, 'fb': False}
[3.1] waiting 3s
[4] requesting go ticket
=> https://github.com/thewoldaa
```

Quiet mode for scripting:

```python
from solver import SafelinkSolver
url = SafelinkSolver(verbose=False).resolve("https://sfl.gl/cgcpp")
```

## How the handshake works

| Step | Endpoint | Notes |
|------|----------|-------|
| 1 | `GET sfl.gl/<alias>` | Page carries `ray_id` + `alias` in a hidden form |
| 2 | `GET app.khaddavi.net/redirect.php` | Sets `__session`, `SESSION`, `XSRF-TOKEN`, `tt` |
| 3 | `POST /api/session` | `_token` = first 39 chars of `XSRF-TOKEN` + `#` + base64(sha256(fingerprint)) |
| 4 | `POST /api/verify` | `{"_a": 0}` after the server-enforced wait |
| 5 | `POST /api/go` | `{"key", "size", "ado"}` returns the `sfl.gl/ready/go` ticket |
| 6 | `GET <ticket>` | Destination sits in a plain `window.location.href` string |

The fingerprint blob is arbitrary — the server only checks that it hashes
consistently into the token. The 10s / 3s waits are enforced server-side, so
they cannot be skipped.

## Limitations

- Links gated behind a passcode or Cloudflare Turnstile raise instead of guessing.
- Site-specific: the ad host (`app.khaddavi.net`) and path layout are tied to
  this particular SafelinkU instance. Other deployments use the same protocol
  with different hosts.

## License

GPL-3.0 — see [LICENSE](LICENSE).
