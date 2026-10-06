#!/bin/sh
# usage: W=<patched zen-control tree> unshare -rmn sh run.sh steps.mjs
set -e
H=$(dirname "$(readlink -f "$0")")
export T=${TMPDIR:-/tmp}/zen-control-test
ip link set lo up
rm -rf $T; mkdir -p $T/profile $T/policies $T/home $T/extension
cp -r $W/extension/. $T/extension/
sed -i 's/allSites: false/allSites: true/' $T/extension/background.js
node -e 'const f=process.argv[1],fs=require("fs");fs.writeFileSync(f,fs.readFileSync(f,"utf8").replace("    case \"ping\":","    case \"zen_tabs\": return await browser.tabs.query({});\n    case \"zen_folder\": return await browser.zenControl.folder((await resolveTab(args.tabId)).id, \"Claude\").then(() => \"ok\", (e) => String(e));\n    case \"zen_debug\": return await browser.zenControl.send((await resolveTab(args.tabId)).id, 0, args.name, args.data);\n    case \"zen_exec\": return (await browser.tabs.executeScript(args.tabId, { code: args.code }))[0];\n    case \"ping\":"))' $T/extension/background.js
cp $W/build-xpi.mjs $T/ && node $T/build-xpi.mjs >/dev/null
printf '{"policies":{"Preferences":{"extensions.experiments.enabled":{"Value":true,"Status":"default"}},"ExtensionSettings":{"zen-control@local":{"installation_mode":"normal_installed","install_url":"file://%s/zen-control.xpi"}}}}' $T > $T/policies/policies.json
mount --bind $T/policies /etc/zen/policies
cat > $T/profile/user.js <<'P'
user_pref("xpinstall.signatures.required", false);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);
user_pref("browser.aboutwelcome.enabled", false);
user_pref("zen.welcome-screen.seen", true);
P
node $H/pages.mjs > $T/pages.log 2>&1 &
PAGES=$!
env -u DBUS_SESSION_BUS_ADDRESS -u WAYLAND_DISPLAY -u DISPLAY HOME=$T/home XDG_CACHE_HOME=$T/home/.cache MOZ_HEADLESS=1 MOZ_HEADLESS_WIDTH=1280 MOZ_HEADLESS_HEIGHT=800 \
  /opt/zen/zen --profile $T/profile --no-remote about:blank > $T/zen.log 2>&1 &
ZEN=$!
node $H/client.mjs "$W" "$@" || true
kill $ZEN $PAGES 2>/dev/null; sleep 1
