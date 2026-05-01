#!/usr/bin/env bash
# Regenerate the over-hard-cap fixture deterministically.
# Output: ~21000 chars (~5250 estimated tokens, English-heavy) — well above 3000-token hard cap.

out="$(dirname "$0")/CLAUDE.md"

{
  echo "# Test Fixture — Over Hard Cap"
  echo
  echo "This fixture deliberately exceeds 3000 estimated tokens (~12000 chars)."
  echo "Used to verify the hard-cap gate refuses additive changes."
  echo
  for i in $(seq 1 60); do
    echo "## Section $i"
    echo
    echo "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod"
    echo "tempor incididunt ut labore et dolore magna aliqua ut enim ad minim"
    echo "veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex"
    echo "ea commodo consequat duis aute irure dolor in reprehenderit in voluptate"
    echo "velit esse cillum dolore eu fugiat nulla pariatur excepteur sint."
    echo
  done
} > "$out"

chars=$(wc -m < "$out")
echo "Generated $out: $chars chars (~$((chars / 4)) estimated tokens, English-heavy)"
