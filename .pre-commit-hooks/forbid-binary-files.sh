#!/bin/bash
# Prevent binary files from being committed

found=0
while IFS= read -r file; do
  if [[ -f "$file" ]] && grep -qI "" "$file" 2>/dev/null; then
    : # text file, ok
  elif [[ -f "$file" ]]; then
    echo "Binary file detected: $file"
    found=1
  fi
done < <(git diff --cached --name-only)

if [[ $found -eq 1 ]]; then
  echo "Commit blocked: remove binary files from staging area with 'git reset HEAD <file>'"
  exit 1
fi
