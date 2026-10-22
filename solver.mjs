#!/usr/bin/env bun
const u = process.argv[2], H = "https://app.khaddavi.net", jar = {};
const take = r => r.headers.getSetCookie().forEach(c => {
  const kv = c.split(";")[0], i = kv.indexOf("=");
  jar[kv.slice(0, i)] = kv.slice(i + 1);
});
const ck = () => Object.entries(jar).map(([k, v]) => `${k}=${v}`).join("; ");

const r0 = await fetch(u); take(r0);
const p = await r0.text();
const q = k => p.match(new RegExp(`name="${k}" value="([^"]+)"`))[1];
const rd = `${H}/redirect.php?ray_id=${q("ray_id")}&alias=${q("alias")}`;
const r1 = await fetch(rd, { redirect: "manual" }); take(r1);
const page = new URL(r1.headers.get("location"), rd).href;
take(await fetch(page, { headers: { cookie: ck() } }));
const o = { cookie: ck(), "content-type": "application/json", referer: page,
  "x-xsrf-token": decodeURIComponent(jar["XSRF-TOKEN"]), origin: H };
await fetch(`${H}/api/verify`, { method: "POST", headers: o, body: '{"_a":0}' });
const g = await fetch(`${H}/api/go`, { method: "POST", headers: o, body: '{"key":1,"size":"3840.2160"}' }).then(r => r.json());
console.log((await (await fetch(g.url)).text()).match(/window\.location\.href = "([^"]+)"/)[1].replaceAll("\\/", "/"));
