#!/usr/bin/env bash
# Fetch and build the pinned third-party runtimes into physics/ (none of them are vendored in this repo).
#
#   physics/hvm2        HVM2 v2.0.22, HigherOrderCO/HVM @ 654276018084b8f44a22b562dd68ab18583bfb5b (Apache-2.0), unmodified
#   physics/hvm2-depth  the same commit + patches/hvm2-depth.patch: same rewrite rules, a round-by-round scheduler that
#                       reports DEPTH / WIDTH / WORK (the "depth oracle"); readback skipped unless GENOME_READBACK is set
#   physics/hvm4        HigherOrderCO/HVM4 @ 6defdfc7dae2a3cca5dd6e74ed0612385b5646a8 (used only by the superposition swings)
#   physics/bend        Bend 0.2.38 (bend-lang from crates.io), installed with cargo into physics/bend/bin
#
# Needs: git, a Rust toolchain (cargo), clang. Tested on macOS (Apple silicon). Usage: scripts/setup_physics.sh [--no-hvm4] [--no-bend]
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
mkdir -p physics scratch

HVM2_URL=${HVM2_URL:-https://github.com/HigherOrderCO/HVM.git}
HVM2_REV=654276018084b8f44a22b562dd68ab18583bfb5b
HVM4_URL=${HVM4_URL:-https://github.com/HigherOrderCO/HVM4.git}
HVM4_REV=6defdfc7dae2a3cca5dd6e74ed0612385b5646a8
BEND_VERSION=0.2.38

WANT_HVM4=1; WANT_BEND=1
for a in "$@"; do
  case "$a" in
    --no-hvm4) WANT_HVM4=0 ;;
    --no-bend) WANT_BEND=0 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

# On macOS the original runs built with the Command Line Tools SDK; harmless elsewhere.
if [[ "$(uname)" == "Darwin" && -d /Library/Developer/CommandLineTools ]]; then
  export DEVELOPER_DIR=/Library/Developer/CommandLineTools
fi

checkout() {  # checkout <url> <rev> <dir>
  local url=$1 rev=$2 dir=$3
  if [[ ! -d "$dir/.git" ]]; then
    git clone --quiet "$url" "$dir"
  fi
  git -C "$dir" fetch --quiet origin "$rev" 2>/dev/null || git -C "$dir" fetch --quiet origin
  git -C "$dir" checkout --quiet --detach "$rev"
  local got; got=$(git -C "$dir" rev-parse HEAD)
  [[ "$got" == "$rev" ]] || { echo "$dir is at $got, expected $rev" >&2; exit 1; }
}

echo "== HVM2 (pinned, unmodified)"
checkout "$HVM2_URL" "$HVM2_REV" physics/hvm2
(cd physics/hvm2 && cargo build --release --quiet)

echo "== HVM2 depth oracle (pinned + patches/hvm2-depth.patch)"
checkout "$HVM2_URL" "$HVM2_REV" physics/hvm2-depth
if git -C physics/hvm2-depth diff --quiet; then
  (cd physics/hvm2-depth && patch -p1 --forward < "$ROOT/patches/hvm2-depth.patch")
else
  echo "physics/hvm2-depth already has local changes; assuming the patch is applied" >&2
fi
(cd physics/hvm2-depth && cargo build --release --quiet)

if [[ $WANT_HVM4 == 1 ]]; then
  echo "== HVM4 (pinned)"
  checkout "$HVM4_URL" "$HVM4_REV" physics/hvm4
  clang -O2 -o physics/hvm4/src/hvm physics/hvm4/src/hvm.c
fi

if [[ $WANT_BEND == 1 ]]; then
  echo "== Bend $BEND_VERSION"
  # The harness only calls `bend gen-hvm`; the generated nets run on physics/hvm2 like every other net.
  cargo install --quiet bend-lang --version "$BEND_VERSION" --root physics/bend
fi

echo "== HERO-5 tracer (vendored, modified HVM2 under genome/hero5/tracer)"
(cd genome/hero5/tracer && cargo build --release --quiet) || echo "tracer build failed (only HERO-5 needs it)" >&2

echo
echo "Built:"
ls -l physics/hvm2/target/release/hvm physics/hvm2-depth/target/release/hvm 2>/dev/null || true
[[ $WANT_HVM4 == 1 ]] && ls -l physics/hvm4/src/hvm || true
[[ $WANT_BEND == 1 ]] && ls -l physics/bend/bin/bend || true
