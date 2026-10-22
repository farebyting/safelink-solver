#!/usr/bin/env bun
const H = "https://app.khaddavi.net", j = {};
const F = async (u, o = {}) => {
  const r = await fetch(new URL(u, H), { ...o, headers: { cookie: Object.entries(j).map(e => e.join("=")).join("; "), ...o.h } });
  r.headers.getSetCookie().forEach(c => { const [k, ...v] = c.split(";")[0].split("="); j[k] = v.join("="); });
  return r;
};
const P = (p, b) => F(p, { method: "POST", body: b, h: { "content-type": "application/json", "x-xsrf-token": j["XSRF-TOKEN"] } }).then(r => r.json());
const h = await (await F(process.argv[2])).text(), m = k => h.match(RegExp(`name="${k}" value="([^"]+)"`))[1];
const r = await F(`/redirect.php?ray_id=${m("ray_id")}&alias=${m("alias")}`, { redirect: "manual" });
await F(r.headers.get("location"));
await P("/api/verify", '{"_a":0}');
console.log((await (await F((await P("/api/go", '{"key":1,"size":"3840.2160"}')).url)).text()).match(/window\.location\.href = "(.+?)"/)[1].replace(/\\/g, ""));
