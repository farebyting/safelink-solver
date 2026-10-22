#!/usr/bin/env bun
const H = "https://app.khaddavi.net"; let ck = "";
const f = async (u, o = {}, h = {}) => {
  const r = await fetch(new URL(u, H), { ...o, headers: { cookie: ck, ...h } }); ck += ";" + r.headers.getSetCookie().map(x => x.split(";")[0]).join(";");
  return r;
};
const q = (u, b) => f(u, { method: "POST", body: b }, { "content-type": "application/json" }).then(r => r.json());
const p = await (await f(process.argv[2])).text(), m = x => p.match(RegExp(`name="${x}" value="([^"]+)"`))[1];
const r = await f(`/redirect.php?ray_id=${m("ray_id")}&alias=${m("alias")}`, { redirect: "manual" });
await f(r.headers.get("location"));
await q("/api/verify", '{"_a":0}');
console.log((await (await f((await q("/api/go", '{"key":1,"size":"3840.2160"}')).url)).text()).match(/href = "(.+?)"/)[1].replace(/\\/g, ""));
