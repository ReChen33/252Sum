#!/usr/bin/env bash

for i in {1..10}; do
  # Use awk for floating‐point multiplication
  result=$(awk -v n="$i" 'BEGIN { print n * 2.5 }')
  echo "$i $result"
done
