import { createServer } from "node:http";
import { readFileSync } from "node:fs";
const dir = new URL("./pages/", import.meta.url).pathname;
createServer((req, res) => {
  const name = req.url.split("?")[0].slice(1) || "index.html";
  try {
    const body = readFileSync(dir + name.replace(/^csp\.html$/, "input.html"));
    const headers = { "content-type": "text/html; charset=utf-8" };
    if (name.startsWith("csp")) headers["content-security-policy"] = "script-src 'self' 'unsafe-inline'";
    res.writeHead(200, headers).end(body);
  } catch { res.writeHead(404).end("nope"); }
}).listen(8000);
