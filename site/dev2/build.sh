#!/bin/bash
# usage: build.sh <out-dir>   stages the site into an empty <out-dir> and builds <out-dir>/_site with the github-pages 232 gem set in ruby:3.3; needs Docker and network
set -euo pipefail
OUT=${1:?out dir}
"$(dirname "$0")/stage.sh" "$OUT"
printf 'source "https://rubygems.org"\ngem "github-pages", "232", group: :jekyll_plugins\ngem "webrick"\n' > "$OUT/Gemfile"
docker run --rm -v "$OUT":/site -e PAGES_REPO_NWO=iamcxa/kc-claude-plugins -e JEKYLL_ENV=production -w /site ruby:3.3 bash -c 'set -o pipefail; bundle config set path /site/vendor/bundle >/dev/null && bundle install --quiet 2>&1 | tail -3 && bundle exec jekyll build --baseurl /kc-claude-plugins 2>&1 | tail -25'
