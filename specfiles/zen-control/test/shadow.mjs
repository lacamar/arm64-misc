export default async (call) => {
  const expect = async (p, want) => { const out = await p; if (!out.includes(want)) console.log(`FAIL: expected ${JSON.stringify(want)}`); return out; };
  const ev = (code) => call("evaluate", { code: "await new Promise(r => setTimeout(r, 200)); " + code });
  await call("tab_new", { url: "http://127.0.0.1:8000/shadow.html" });
  await expect(call("read_page", {}), 'textbox "Shadow field"');
  await expect(call("find", { query: "shadow field" }), "textbox");
  await call("click", { x: 10, y: 110 });
  await call("type", { text: "yo" });
  await expect(ev("si.value"), "yo");
  await call("click", { x: 60, y: 175 });
  await expect(ev("log.splice(0).join(' ')"), "fclick:T");
  await call("click", { x: 30, y: 220 });
  await call("press_key", { key: "Enter" });
  await expect(ev("log.splice(0).join(' ')"), "fkey:Enter:T");
  await call("scroll", { x: 100, y: 40, amount: 100 });
  await expect(ev("sc.scrollTop"), "100");
};
