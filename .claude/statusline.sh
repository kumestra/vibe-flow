#!/bin/bash

fmt_remain() {
  local diff=$(( $1 - $(date +%s) ))
  if   (( diff <= 0 ));     then echo "soon"
  elif (( diff < 3600 ));   then echo "$((diff / 60))m"
  elif (( diff < 86400 ));  then echo "$((diff / 3600))h$(( (diff % 3600) / 60 ))m"
  else echo "$((diff / 86400))d$(( (diff % 86400) / 3600 ))h$(( (diff % 3600) / 60 ))m"
  fi
}

IFS=$'\t' read -r model max pct rl5h rl5h_resets rl7d rl7d_resets < <(jq -r '
  [
    (.model.display_name // "Unknown"),
    (.context_window.context_window_size // 0),
    (.context_window.used_percentage // 0),
    (.rate_limits.five_hour.used_percentage // ""),
    (.rate_limits.five_hour.resets_at // ""),
    (.rate_limits.seven_day.used_percentage // ""),
    (.rate_limits.seven_day.resets_at // "")
  ] | @tsv
')

used=$(( (max * ${pct%.*}) / 100 ))
output="$model | $((used / 1000))k/$((max / 1000))k tokens (${pct%.*}%)"

if [[ -n "$rl5h" ]]; then
  output+=" | 5h: ${rl5h%.*}% (reset $(fmt_remain $rl5h_resets)) 7d: ${rl7d%.*}% (reset $(fmt_remain $rl7d_resets))"
fi

echo "$output"
