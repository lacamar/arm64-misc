export default async (call, raw) => {
  const t = JSON.parse(await call("tab_new", { url: "http://127.0.0.1:8000/input.html" })).id;
  const vis = await call("evaluate", { code: "await Promise.race([new Promise((r) => requestAnimationFrame(() => r('raf'))), new Promise((r) => setTimeout(() => r('no-raf'), 3000))]) + '|' + document.visibilityState" });
  if (!vis.includes("raf|visible")) console.log("FAIL: background tab not visible: " + vis);
  if (String(await call("tabs_list")).includes(`${t} (active)`)) console.log("FAIL: tab was shown");
  await call("tab_select", { tabId: t, activate: true });
  if (String(await call("tabs_list")).includes(`${t} (active)`)) console.log("FAIL: activate still shows the tab");
};
