import { existsSync } from "node:fs";
export default async (call, raw) => {
  const expect = async (p, want, not) => { const out = String(await p); if (out.includes(want) === !!not) console.log(`FAIL: expected ${not ? "no " : ""}${JSON.stringify(want)}`); return out; };
  const t = JSON.parse(await call("tab_new", { url: "http://127.0.0.1:8000/input.html" })).id;
  await raw("tab_new", { url: "http://127.0.0.1:8000/frames.html" });
  await expect(call("tabs_list"), `* ${t} `);
  await expect(call("tabs_list"), "frames.html", true);
  await expect(call("tabs_list", { query: "FRAMES" }), "frames.html");
  await expect(call("tabs_list", { all: true }), "frames.html");

  await call("evaluate", { code: `const a = document.createElement("a"); a.id = "dl"; a.href = "/frame.html"; a.download = "x.txt"; a.textContent = "dl"; document.body.append(a); 1` });
  await call("click", { selector: "#dl" });
  const d = JSON.parse(await expect(call("downloads", { wait: true, timeout: 10000 }), '"state": "complete"'));
  if (!d[0].file.endsWith("x.txt") || !existsSync(d[0].file)) console.log("FAIL: download path " + d[0].file);

  const pill = `document.querySelector("zen-control-marker").openOrClosedShadowRoot`;
  const h = call("handoff", { message: "Log in please", selector: "input" });
  await new Promise((r) => setTimeout(r, 1000));
  await expect(raw("zen_exec", { tabId: t, code: `${pill}.querySelector("span").textContent + "|" + document.querySelector("input").style.outline` }), "Claude needs you: Log in please|rgb(37, 99, 235) solid 3px");
  await raw("zen_exec", { tabId: t, code: `${pill}.querySelector(".main").click(); 1` });
  await expect(h, '"user": "done"');
  await expect(raw("zen_exec", { tabId: t, code: `${pill}.querySelector("span").textContent + "|" + document.querySelector("input").getAttribute("style")` }), "controlling this tab|null");
  const h2 = call("handoff", { message: "Solve it" });
  await new Promise((r) => setTimeout(r, 500));
  await raw("zen_exec", { tabId: t, code: `${pill}.querySelector(".skip").click(); 1` });
  await expect(h2, '"user": "skipped"');
  await expect(call("handoff", { message: "x", timeout: 1500 }), '"user": "timeout"');
};
