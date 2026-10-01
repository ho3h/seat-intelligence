#!/usr/bin/env bash
# Pre-release check: secret scan + size report over the files git would ship.
# Exit 1 if a likely secret is found, a forbidden path is tracked, or a file is over the size limit.
# Usage: scripts/check_release.sh [--all]   (--all scans the working tree instead of `git ls-files`)
set -uo pipefail
cd "$(dirname "$0")/.."
MAX_FILE_MB=${MAX_FILE_MB:-20}
MAX_TOTAL_MB=${MAX_TOTAL_MB:-60}
status=0

if [[ "${1:-}" != "--all" ]] && git rev-parse --git-dir >/dev/null 2>&1 && [[ -n "$(git ls-files | head -1)" ]]; then
  list() { git ls-files -z; }
  echo "Scanning tracked files ($(git ls-files | wc -l | tr -d ' '))"
else
  list() { find . -type f -not -path './.git/*' -not -path './physics/*' -not -path './scratch/*' | sed 's|^\./||' | tr '\n' '\0'; }
  echo "Scanning working tree (physics/ and scratch/ skipped)"
fi

echo
echo "== 1. Likely secrets (high confidence: key-shaped strings)"
# key formats: OpenAI/Anthropic/OpenRouter (sk-...), GitHub (ghp_/gho_/ghs_/github_pat_), Hugging Face (hf_), AWS (AKIA), bearer headers with a value
STRONG='(^|[^A-Za-z0-9_-])(sk-(ant-|or-v1-|proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|hf_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|Authorization: Bearer [A-Za-z0-9._-]{16,}|-----BEGIN [A-Z ]*PRIVATE KEY-----))'
hits=$(list | xargs -0 grep -IEno "$STRONG" 2>/dev/null || true)
if [[ -n "$hits" ]]; then echo "$hits" | head -50; echo "FAIL: key-shaped strings found"; status=1; else echo "none"; fi

echo
echo "== 2. Secret-adjacent words (review by eye; references in code are expected)"
list | xargs -0 grep -IEnoi "(api_key|OPENROUTER[A-Z_]*|ANTHROPIC_API_KEY|Authorization: Bearer|\bsk-|\bgho_|\bghp_|\bhf_[A-Za-z]|AKIA)" 2>/dev/null \
  | awk -F: '{print $1": "$3}' | sort | uniq -c | sort -rn | head -40 || true

echo
echo "== 3. Forbidden paths"
bad=$(list | tr '\0' '\n' | awk '
  /(^|\/)\.env($|\.)/ || /(^|\/)\.DS_Store$/ || /__pycache__\// || /\.pyc$/ || /\.pt$/ || /(^|\/)node_modules\// {print; next}
  /^data\// && !/^data\/hero\/(luncheon\.json|policies_test[0-9]*\.json)$/ {print; next}
  /^adapters\// && !/^adapters\/README\.md$/ {print; next}
  /^physics\// {print; next}
  /^scratch\// && !/^scratch\/\.gitkeep$/ {print; next}')
if [[ -n "$bad" ]]; then echo "$bad" | head -30; echo "FAIL: forbidden paths present"; status=1; else echo "none"; fi

echo
echo "== 4. Sizes"
total=0; big=0
while IFS= read -r -d '' f; do
  s=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f"); total=$((total + s))
  if (( s > MAX_FILE_MB * 1024 * 1024 )); then echo "TOO BIG: $f ($s bytes)"; big=1; fi
done < <(list)
printf "total %.1f MB (limit %d MB), per-file limit %d MB\n" "$(echo "$total/1048576" | bc -l)" "$MAX_TOTAL_MB" "$MAX_FILE_MB"
(( big )) && status=1
(( total > MAX_TOTAL_MB * 1024 * 1024 )) && { echo "FAIL: total over limit"; status=1; }
echo "largest 15:"
list | xargs -0 ls -l 2>/dev/null | awk '{print $5"\t"$NF}' | sort -rn | head -15

echo
echo "== 5. Machine-specific absolute paths (informational)"
n=$(list | xargs -0 grep -Il "/Users/" 2>/dev/null | wc -l | tr -d ' ')
echo "$n files mention /Users/ (should be only docs that quote paths; run records use <home>, code is repo-relative)"
list | xargs -0 grep -Il "/Users/" 2>/dev/null | grep -E '^(genome|demo|scripts)/' | head -10

echo
[[ $status == 0 ]] && echo "check_release: OK" || echo "check_release: FAILED"
exit $status
