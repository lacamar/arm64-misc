import { utimesSync } from "node:fs";
export default async (call, raw) => {
  const expect = async (p, want) => { const out = await p; if (!out.includes(want)) console.log(`FAIL: expected ${JSON.stringify(want)}`); return out; };
  await call("tab_new", { url: "http://127.0.0.1:8000/input.html" });
  await raw("tab_new", { url: "http://127.0.0.1:8000/frames.html" });
  await expect(call("read_page", { filter: "interactive" }), "input.html");
  await expect(call("browser_status"), '"extension": "0.1.2.10"');
  const g = (await raw("zen_tabs")).filter((t) => t.url.startsWith("http"));
  if (g.length !== 2 || g[0].groupId === g[1].groupId || g.some((t) => t.groupId === -1)) console.log("FAIL: per-session folders " + JSON.stringify(g.map((t) => [t.url, t.groupId])));
  utimesSync(process.argv[2] + "/server/index.js", new Date(), new Date());
  await expect(call("browser_status"), "was upgraded");
};
