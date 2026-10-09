export default async (call, raw) => {
  const expect = async (p, want, not) => { const out = String(await p); if (out.includes(want) === !!not) console.log(`FAIL: expected ${not ? "no " : ""}${JSON.stringify(want)}`); return out; };
  const t = JSON.parse(await call("tab_new", { url: "http://127.0.0.1:8000/input.html" })).id;
  await expect(raw("zen_exec", { tabId: t, code: `(async () => {
    const p = document.querySelector("zen-control-marker").openOrClosedShadowRoot, w = () => new Promise((r) => setTimeout(r, 300)), s = p.querySelector(".skip");
    p.querySelector(".main").click(); await w();
    const a = p.querySelector("span").textContent + "|" + s.textContent + "|" + s.hidden;
    s.click(); await w();
    return a + "|" + !!document.querySelector("zen-control-marker")?.isConnected + "|" + document.title.startsWith("🤖");
  })()` }), "stopped on this tab|Remove|false|false|false");
  await expect(call("tabs_list"), `  ${t} `, true);
  await expect(call("get_text", { tabId: t }), "stopped", true);
  await expect(raw("zen_exec", { tabId: t, code: `!!document.querySelector("zen-control-marker")?.isConnected` }), "true");
};
