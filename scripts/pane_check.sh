#!/bin/bash
for s in canitford ford; do
  for i in 0 1 2 3 4 5; do
    echo "=== $s pane $i ==="
    tmux capture-pane -t $s:0.$i -p -S -50
  done
done
