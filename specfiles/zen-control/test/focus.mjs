export default async (call, raw) => {
  const t = JSON.parse(await call("tab_new", { url: "http://127.0.0.1:8000/input.html", active: true })).id;
  await call("evaluate", { code: "addEventListener('click', () => window.focus()); 1" });
  const w2 = String(await raw("zen_win"));
  await new Promise((r) => setTimeout(r, 1000));
  await call("click", { selector: "#b" });
  await new Promise((r) => setTimeout(r, 1000));
  if (String(await raw("zen_focused")) !== w2) console.log("FAIL: window focus stolen");
  if (!String(await call("evaluate", { code: "log.join()" })).includes("click:b:T")) console.log("FAIL: click lost");
};
