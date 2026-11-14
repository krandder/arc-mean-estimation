#!/bin/bash
# usage: fetch_forum.sh OUTDIR ID...
# Fetches discourse raw markdown and topic JSON for each topic id; logs UTC fetch time.
out="$1"; shift
for id in "$@"; do
  curl -sS -A 'Mozilla/5.0' -o "$out/raw$id.txt" "https://discourse.aicrowd.com/raw/$id"
  curl -sS -A 'Mozilla/5.0' -o "$out/t$id.json" "https://discourse.aicrowd.com/t/$id.json"
  echo "$id $(date -u +%FT%TZ) raw=$(stat -c %s "$out/raw$id.txt") json=$(stat -c %s "$out/t$id.json")" >> "$out/fetch.log"
  sleep 0.7
done
