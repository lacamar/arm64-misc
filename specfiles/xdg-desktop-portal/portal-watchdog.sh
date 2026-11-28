#!/usr/bin/bash
MAX_THREADS=${PORTAL_MAX_THREADS:-64}
MAX_MEMORY_STALL=${PORTAL_MAX_MEMORY_STALL:-10}
PSI_MEMORY=${PSI_MEMORY:-/proc/pressure/memory}

probe() {
  timeout 5 gdbus call --session --dest org.freedesktop.portal.Desktop \
    --object-path /org/freedesktop/portal/desktop \
    --method org.freedesktop.portal.Settings.Read org.freedesktop.appearance color-scheme >/dev/null 2>&1
}

log_callers() {
  timeout 20 stdbuf -oL dbus-monitor --session "destination='org.freedesktop.portal.Desktop'" 2>/dev/null |
    sed -unE 's/.*method call.*sender=([^ ]+).*member=(.*)/\1 \2/p' |
    while read -r sender member; do
      p=$(busctl --user call org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus \
        GetConnectionUnixProcessID s "$sender" 2>/dev/null | awk '{print $2}')
      cmd=$([[ $p ]] && tr '\0' ' ' </proc/$p/cmdline 2>/dev/null | cut -c1-120)
      echo "caller $member pid=${p:-gone} ppid=$([[ $p ]] && awk '/^PPid/{print $2}' /proc/$p/status 2>/dev/null) $cmd"
    done | sort | uniq -c
}

restart() {
  stall=$(awk -F'[= ]' '/^full/{print int($3)}' "$PSI_MEMORY" 2>/dev/null)
  if (( ${stall:-0} >= MAX_MEMORY_STALL )); then
    echo "xdg-desktop-portal (pid $pid, $threads threads) $1 under ${stall}% memory stall; not restarting"
    exit 0
  fi
  echo "xdg-desktop-portal (pid $pid, $threads threads) $1; dumping core and restarting"
  log_callers
  systemctl --user kill -s ABRT xdg-desktop-portal
  systemctl --user kill -s CONT xdg-desktop-portal
  sleep 3
  systemctl --user kill -s KILL xdg-desktop-portal 2>/dev/null
  systemctl --user restart xdg-desktop-portal
  notify-send -a portal-watchdog "xdg-desktop-portal was $1" "Restarted; core in coredumpctl, callers in journalctl --user -u portal-watchdog" || true
  exit 0
}

systemctl --user -q is-active xdg-desktop-portal || exit 0
pid=$(systemctl --user show -p MainPID --value xdg-desktop-portal)
threads=$(ls /proc/$pid/task 2>/dev/null | wc -l)
echo "threads=$threads"
(( threads > MAX_THREADS )) && restart "leaking threads"
probe && exit 0
sleep 10
probe && exit 0
restart "hung"
