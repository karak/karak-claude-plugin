#!/usr/bin/env bash
# Translate PlusCal (if present), parse with SANY, then model-check with TLC.
# Usage: bash tlc.sh Spec.tla [Spec.cfg] [extra TLC args...]
# Needs Java 11+ and tla2tools.jar; set TLA2TOOLS to its path.
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "usage: bash $0 Spec.tla [Spec.cfg] [extra TLC args...]" >&2
  exit 2
fi

JAR="${TLA2TOOLS:-}"
if [ -z "$JAR" ] || [ ! -f "$JAR" ]; then
  echo "TLA2TOOLS is not set to an existing tla2tools.jar." >&2
  echo "Get it from https://github.com/tlaplus/tlaplus/releases and export TLA2TOOLS=/path/to/tla2tools.jar" >&2
  exit 2
fi

SPEC="$1"; shift
DIR="$(cd "$(dirname "$SPEC")" && pwd)"
BASE="$(basename "$SPEC" .tla)"
CFG="$DIR/$BASE.cfg"
if [ $# -gt 0 ] && [[ "$1" == *.cfg ]]; then
  CFG="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; shift
fi

cd "$DIR"

if grep -q -- '--algorithm\|--fair algorithm' "$BASE.tla"; then
  echo "== pcal.trans $BASE.tla"
  # -nocfg: keep the hand-written .cfg instead of overwriting it
  PCAL_OUT="$(java -cp "$JAR" pcal.trans -nocfg "$BASE.tla" 2>&1)" || { echo "$PCAL_OUT"; exit 1; }
  if ! grep -q 'Translation completed' <<<"$PCAL_OUT"; then echo "$PCAL_OUT"; exit 1; fi
  rm -f "$BASE.old"   # pcal.trans keeps a backup of the previous file
fi

echo "== SANY $BASE.tla"
SANY_OUT="$(java -cp "$JAR" tla2sany.SANY "$BASE.tla" 2>&1)" || { echo "$SANY_OUT"; exit 1; }
# match SANY's failure banners only: paths and module names may contain "error"
if grep -qE 'Semantic errors|Fatal errors|Abort messages|^\*\*\* Errors|Parse Error|Lexical error' <<<"$SANY_OUT"; then
  echo "$SANY_OUT"; exit 1
fi

echo "== TLC $BASE.tla -config $(basename "$CFG") $*"
# keep TLC's states/ directory and trace files out of the repo
META="$(mktemp -d)"
trap 'rm -rf "$META"' EXIT
java -XX:+UseParallelGC -cp "$JAR" tlc2.TLC -metadir "$META" -workers auto -config "$CFG" "$@" "$BASE.tla"
