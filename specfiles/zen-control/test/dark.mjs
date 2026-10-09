import { execFileSync } from "node:child_process";
const px = (out) => execFileSync("magick", [out.match(/<image (\S+)>/)[1], "-format", "%[fx:int(255*r)],%[fx:int(255*g)],%[fx:int(255*b)]", "-crop", "1x1+5+5", "info:"]).toString();
export default async (call) => {
  const check = async (args) => { const c = px(await call("screenshot", args)); if (Math.max(...c.split(",").map(Number)) > 100) console.log(`FAIL: light canvas ${c} for ${JSON.stringify(args)}`); else console.log(`ok ${c}`); };
  const t = JSON.parse(await call("tab_new", { url: "http://127.0.0.1:8000/dark.html" })).id;
  await check({ tabId: t });
  await check({ tabId: t, region: [0, 0, 300, 100] });
  const l = JSON.parse(await call("tab_new", { url: "http://127.0.0.1:8000/input.html" })).id;
  const c = px(await call("screenshot", { tabId: l }));
  console.log(c === "255,255,255" ? "ok light" : `FAIL: light page ${c}`);
};
