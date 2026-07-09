#!/bin/bash
# Publish the site to GitHub Pages.
# Usage: bash _build/publish.sh "commit message"
set -e
cd "$(dirname "$0")/.."
MSG="${1:-Update site}"
TOKEN=$(cat token/git-token | tr -d '[:space:]')
git add -A
git commit -m "$MSG" || echo "nothing to commit"
git push "https://nrm461:${TOKEN}@github.com/nrm461/nrm461.github.io.git" main
echo "Published: https://nrm461.github.io"
