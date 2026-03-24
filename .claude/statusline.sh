#!/bin/bash
jq -r '
  (.model.display_name // "Unknown") as $model |
  (.context_window.context_window_size // 0) as $max |
  (.context_window.used_percentage // 0) as $pct |
  (($max * $pct / 100) | round) as $used |
  "\($model) | \($used / 1000 | floor)k/\($max / 1000 | floor)k tokens (\($pct | round)%)"
'
