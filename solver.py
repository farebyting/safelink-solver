#!/usr/bin/env python3
import json
import re
import sys
from urllib.parse import unquote

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
HOST = "https://app.khaddavi.net"


def resolve(url):
    s = requests.Session()
    s.headers["User-Agent"] = UA

    page = s.get(url, timeout=25).text
    ray = re.search(r'name="ray_id" value="([^"]+)"', page).group(1)
    alias = re.search(r'name="alias" value="([^"]+)"', page).group(1)

    landed = s.get(f"{HOST}/redirect.php", params={"ray_id": ray, "alias": alias}, timeout=25)
    xsrf = unquote([c.value for c in s.cookies
                    if c.name == "XSRF-TOKEN" and "khaddavi" in c.domain][-1])
    h = {"Content-Type": "application/json", "X-XSRF-TOKEN": xsrf, "Origin": HOST,
         "Referer": landed.url, "X-Requested-With": "XMLHttpRequest"}

    s.post(f"{HOST}/api/verify", json={"_a": 0}, headers=h, timeout=25)
    go = s.post(f"{HOST}/api/go", json={"key": 1, "size": "3840.2160"},
                headers=h, timeout=25).json()

    dest = re.search(r'window\.location\.href\s*=\s*"([^"]+)"',
                     s.get(go["url"], headers=h, timeout=25).text)
    return dest.group(1).replace("\\/", "/")


if __name__ == "__main__":
    print(resolve(sys.argv[1]))
