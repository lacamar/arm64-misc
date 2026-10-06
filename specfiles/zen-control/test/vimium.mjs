export default async (call, raw) => {
  const expect = async (p, want) => { const out = String(await p); if (!out.includes(want)) console.log(`FAIL: expected ${JSON.stringify(want)} in ${out.slice(0, 300)}`); return out; };
  const t = JSON.parse(await call("tab_new", { url: "http://127.0.0.1:8000/input.html" })).id;
  await raw("zen_exec", { tabId: t, code: `window.stolen = 0; for (const ty of ["keydown", "keypress", "keyup", "mousedown", "click"]) window.addEventListener(ty, (e) => { stolen++; e.preventDefault(); e.stopImmediatePropagation(); }, true); 1` });
  await call("click", { selector: "#t" });
  await call("press_key", { key: "x" });
  await call("type", { selector: "#t", text: "yz", clear: false });
  await call("click", { selector: "#b" });
  await expect(call("evaluate", { code: `t.value + "|" + log.filter((l) => /^(keydown:t|click:b)/.test(l)).length` }), "xyz|4");
  await raw("zen_exec", { tabId: t, code: `window.dispatchEvent(new KeyboardEvent("keydown")); 1` });
  await expect(raw("zen_exec", { tabId: t, code: `stolen` }), "1");
};
