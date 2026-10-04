import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";

const W = resolve(process.argv[2]), req = createRequire(W + "/package.json");
const { Client } = req("@modelcontextprotocol/sdk/client/index.js");
const { StdioClientTransport } = req("@modelcontextprotocol/sdk/client/stdio.js");
const { WebSocket } = req("ws");
const client = new Client({ name: "harness", version: "0" });
await client.connect(new StdioClientTransport({ command: "node", args: [W + "/server/index.js"], stderr: "ignore" }));
let shot = 0;
async function call(name, args = {}, quiet) {
  const r = await client.callTool({ name, arguments: args });
  const out = r.content.map((c) => {
    if (c.type !== "image") return c.text;
    const f = `${process.env.T}/shot${++shot}.png`;
    writeFileSync(f, Buffer.from(c.data, "base64"));
    return `<image ${f}>`;
  }).join("\n");
  if (!quiet) console.log(`\n### ${name} ${JSON.stringify(args)}${r.isError ? " ERROR" : ""}\n${out}`);
  return out;
}
for (let i = 0; i < 60; i++) {
  if ((await call("browser_status", {}, true)).includes('"connected": true')) break;
  await new Promise((r) => setTimeout(r, 500));
}
const ctl = new WebSocket("ws://127.0.0.1:17373/ctl");
await new Promise((r) => ctl.on("open", r));
let rid = 0;
function raw(cmd, args = {}) {
  const id = "raw-" + ++rid;
  ctl.send(JSON.stringify({ type: "cmd", id, cmd, args }));
  return new Promise((r) => ctl.on("message", function f(d) { const m = JSON.parse(d); if (m.id === id) { ctl.off("message", f); console.log(`\n### raw ${cmd} ${JSON.stringify(args)}\n${JSON.stringify(m.ok ? m.result : "ERROR " + m.error)}`); r(m.result); } }));
}
const steps = await import(resolve(process.argv[3]));
try { await steps.default(call, raw); } catch (e) { console.log("STEPS FAILED", e); }
await client.close();
process.exit(0);
