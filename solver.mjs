const H = "https://app.khaddavi.net"
const p = await (await fetch(process.argv[2])).text(), ray = p.match(/ray_id" value="([^"]+)/)[1], al = p.match(/alias" value="([^"]+)/)[1]
const C = ["__session=" + ray], f = async (u, o = {}) => { const r = await fetch(new URL(u, H), { ...o, headers: { cookie: C.join(";"), ...o.h } }); C.push(...r.headers.getSetCookie().map(x => x.split(";")[0])); return r }; await f(`/redirect.php?ray_id=${ray}&alias=${al}`)
const q = (a, b) => f("/api/" + a, { method: "POST", body: b, h: { "content-type": "application/json" } }).then(r => r.json()); await q("verify", '{"_a":0}')
console.log((await (await f((await q("go", '{"key":1,"size":"3840.2160"}')).url)).text()).match(/href = "(.+?)"/)[1].replace(/\\/g, ""))
