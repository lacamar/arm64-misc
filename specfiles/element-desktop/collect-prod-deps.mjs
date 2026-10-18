import fs from "node:fs";
import path from "node:path";
const [pkgDir, skip] = [process.argv[2], new Set(process.argv.slice(3))];
const entries = new Set();
const seen = new Set();
const walk = (dir) => {
    const p = JSON.parse(fs.readFileSync(path.join(dir, "package.json")));
    const base = dir === pkgDir ? path.join(dir, "node_modules") : dir.slice(0, dir.lastIndexOf("/node_modules/") + 13);
    for (const name of Object.keys({ ...p.dependencies, ...p.optionalDependencies, ...p.peerDependencies })) {
        if (skip.has(name)) continue;
        const link = path.join(base, name);
        if (!fs.existsSync(link)) continue;
        const real = fs.realpathSync(link);
        if (seen.has(real)) continue;
        seen.add(real);
        entries.add(real.match(/\.pnpm\/([^/]+)\//)[1]);
        walk(real);
    }
};
walk(pkgDir);
console.log([...entries].join("\n"));
