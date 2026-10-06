export default async (call, raw) => {
  const expect = async (p, want) => { const out = await p; if (!out.includes(want)) console.log(`FAIL: expected ${JSON.stringify(want)}`); return out; };
  const L = () => call("evaluate", { code: "await new Promise(r => setTimeout(r, 200)); log.splice(0).join(' ')" });
  await call("tab_new", { url: "http://127.0.0.1:8000/frames.html" });
  const page = await expect(call("read_page", {}), 'button "Frame button"');
  const ref = (re) => page.match(re)?.[1];
  const fb = ref(/\[(f\d+:e\d+)\] button/), fi = ref(/\[(f\d+:e\d+)\] textbox/);
  await call("click", { ref: fb }); await expect(L(), "fclick:T");
  await call("type", { ref: fi, text: "hi" }); await expect(L(), "finput:hi");
  await call("press_key", { key: "Enter" }); await expect(L(), "fkey:Enter:T");
  await call("click", { x: 50 + 2 + 60, y: 100 + 2 + 25 }); await expect(L(), "fclick:T");
  await expect(call("find", { query: "frame button" }), fb);
  await expect(call("read_page", { ref: fi }), "Frame input");
  await expect(call("screenshot", { ref: fb }), "Area 100x30 CSS px at page (62, 112)");
  await call("tab_new", { url: "http://127.0.0.1:8000/input.html" });
  const g = (await raw("zen_tabs")).filter((t) => t.url.startsWith("http"));
  if (g.length !== 2 || !g.every((t) => t.pinned && t.groupId === g[0].groupId && t.groupId !== -1)) console.log("FAIL: Claude folder " + JSON.stringify(g.map((t) => [t.pinned, t.groupId])));
};
