#!/usr/bin/env python3
"""
SafelinkU / sfl.gl pure-HTTP ad-link resolver.
No browser, no JS, no Selenium. Just the cookie handshake the site expects.
"""
import base64
import hashlib
import json
import re
import sys
import time
from urllib.parse import unquote, urljoin

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# Any stable blob works; the server only checks that it's formatted/hashed.
FINGERPRINT = (
    "webgl:Google Inc. (NVIDIA)||audio:124.04347527516074||canvas:c0ffee||"
    "fonts:andale mono|arial||system:Win32|Win64||env:1920x1080|24||"
    "network:4g|10|50"
)


class SafelinkSolver:
    def __init__(self, timeout=25, verbose=True):
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": UA,
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.timeout = timeout
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    # ---- token --------------------------------------------------------
    def _xsrf(self):
        vals = [unquote(c.value) for c in self.s.cookies
                if c.name == "XSRF-TOKEN" and "khaddavi" in c.domain]
        if not vals:
            return None
        return vals[-1]

    def _token(self):
        core = hashlib.sha256(FINGERPRINT.encode()).hexdigest()
        suffix = "#" + base64.b64encode(core.encode()).decode()
        return self._xsrf()[:128 - len(suffix)] + suffix

    def _headers(self, referer):
        return {
            "Content-Type": "application/json",
            "Origin": "https://app.khaddavi.net",
            "Referer": referer,
        }

    # ---- hops ---------------------------------------------------------
    def _follow(self, url, referer=None, limit=8):
        for _ in range(limit):
            h = {"Referer": referer} if referer else {}
            r = self.s.get(url, headers=h, timeout=self.timeout,
                           allow_redirects=False)
            if r.status_code in (301, 302, 303, 307, 308):
                url = urljoin(url, r.headers["Location"])
                continue
            return url, r
        return url, r

    def _api(self, path, payload, referer):
        r = self.s.post("https://app.khaddavi.net" + path,
                        data=json.dumps(payload),
                        headers=self._headers(referer),
                        timeout=self.timeout)
        try:
            return r.status_code, r.json()
        except ValueError:
            return r.status_code, {"raw": r.text}

    # ---- main ---------------------------------------------------------
    def resolve(self, short_url, max_passes=4):
        p = lambda *a: self.log("  ".join(str(x) for x in a))

        # 1. entry page hands over ray_id + alias
        r = self.s.get(short_url, timeout=self.timeout)
        ray = re.search(r'name="ray_id"\s+value="([^"]+)"', r.text)
        alias = re.search(r'name="alias"\s+value="([^"]+)"', r.text)
        if not ray or not alias:
            raise RuntimeError("entry page did not expose ray_id/alias")
        ray_id, alias = ray.group(1), alias.group(1)
        p("[1] ray_id:", ray_id, "alias:", alias)

        # 2. land on the ad host, collect session cookies
        landed, _ = self._follow(
            "https://app.khaddavi.net/redirect.php?ray_id=%s&alias=%s" % (ray_id, alias),
            referer=short_url,
        )
        p("[2] landed:", landed)
        if not self._xsrf():
            raise RuntimeError("no XSRF cookie on ad host")

        # 3. session -> wait -> verify (this only advances the ad state)
        for n in range(max_passes):
            code, cfg = self._api("/api/session", {"_token": self._token()}, landed)
            p("[3.%d] session:" % n, cfg)
            if cfg.get("passcode") or cfg.get("captcha"):
                raise RuntimeError("link is gated: %s" % cfg)
            wait = 10 if cfg.get("step") == 1 else 3
            p("[3.%d] waiting %ss" % (n, wait))
            time.sleep(wait)
            code, ver = self._api("/api/verify", {"_a": 0}, landed)
            p("[3.%d] verify:" % n, ver)
            if cfg.get("step") == 2:
                break

        # 4. the go endpoint hands out the real shortener ticket
        p("[4] requesting go ticket")
        code, go = self._api(
            "/api/go",
            {"key": 123, "size": "3840.2160", "ado": ""},
            landed,
        )
        p("[4] go:", go)
        ticket = go.get("url")
        if not ticket:
            raise RuntimeError("no go url: %r" % go)

        # 5. final gate page; destination is embedded in its script
        page = self.s.get(ticket, headers={"Referer": landed},
                          timeout=self.timeout).text
        m = re.search(r'window\.location\.href\s*=\s*"([^"]+)"', page)
        if not m:
            m = re.search(r'href="(https?://(?!safelinku|sfl\.gl)[^"]+)"', page)
        if not m:
            raise RuntimeError("destination not found on gate page")
        return m.group(1).replace(chr(92)+chr(47), chr(47))


def main():
    if len(sys.argv) < 2:
        print("usage: solver.py <adlink>", file=sys.stderr)
        return 1
    dest = SafelinkSolver().resolve(sys.argv[1])
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
