#!/usr/bin/env bash
# Publishes files to the rolling `nightly` prerelease.
#
#   publish-nightly.sh <component> <summary> <file>...
#
# Both Flutter-build.yml and Python-build.yml call this, each for its own
# files. Asset names are fixed so download URLs never change, and --clobber
# replaces the previous night's copy. The release notes keep one line per
# component, so one workflow never wipes out what the other wrote.
#
# The release must stay a prerelease: Config.py reads /releases/latest and
# parses the tag as a float, which "nightly" is not. /releases/latest never
# returns a prerelease.
#
# Callers must serialise on `concurrency: nightly-release`, otherwise two runs
# can both see "no release" and race to create it.
#
# Needs GH_TOKEN (contents: write) and a checkout whose origin can be pushed to.

set -euo pipefail

if (( $# < 3 )); then
  echo 'Usage: publish-nightly.sh <component> <summary> <file>...' >&2
  exit 2
fi
TAG=nightly
component=$1
summary=$2
shift 2

[[ "$component" =~ ^[A-Za-z][A-Za-z0-9_-]*$ ]] || { echo 'Invalid component' >&2; exit 2; }
: "${GITHUB_SHA:?}" "${GITHUB_SERVER_URL:?}" "${GITHUB_REPOSITORY:?}" "${GITHUB_RUN_ID:?}"
[[ "$GITHUB_SHA" =~ ^[0-9a-fA-F]{40}$ ]] || { echo 'Invalid commit' >&2; exit 2; }
for artifact in "$@"; do
  [[ -f "$artifact" && -s "$artifact" ]] || { echo "Missing or empty artifact: $artifact" >&2; exit 1; }
done

# Read the current notes before publishing anything. A network/authentication
# failure is not evidence that the release is absent and must not erase notes.
body_file=$(mktemp)
error_file=$(mktemp)
notes_file=$(mktemp)
trap 'rm -f -- "$body_file" "$error_file" "$notes_file"' EXIT
if ! gh api "repos/${GITHUB_REPOSITORY}/releases/tags/${TAG}" --jq '.body // ""' > "$body_file" 2> "$error_file"; then
  if ! grep -q 'HTTP 404' "$error_file"; then
    cat "$error_file" >&2
    exit 1
  fi
  printf '%s\n' 'master 每次推送自動建置。檔名固定，下載網址不會變。' > "$body_file"
  gh release create "${TAG}" --prerelease --title "Nightly" \
    --target "${GITHUB_SHA}" --notes-file "$body_file"
fi

gh release upload "${TAG}" --clobber -- "$@"

# Replace this component's line in the notes, keep everything else.
line="- **${component}**: ${summary} · $(date -u +'%Y-%m-%d %H:%M UTC') · ${GITHUB_SHA::7} · [run](${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID})"
awk -v prefix="- **${component}**:" 'index($0, prefix) != 1' "$body_file" > "$notes_file"
printf '%s\n' "$line" >> "$notes_file"
gh release edit "${TAG}" --prerelease --notes-file "$notes_file"

# Only move an existing tag once this component's artifacts and notes arrived.
# Fixed-name asset replacement itself is not an atomic multi-file transaction.
git tag -f "${TAG}" "${GITHUB_SHA}"
git push -f origin "refs/tags/${TAG}"
