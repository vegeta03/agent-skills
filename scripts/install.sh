#!/usr/bin/env bash
set -euo pipefail

REPO="vegeta03/agent-skills"
REF="master"
TARGET="all"
INVOCATION="both"
WORKSPACE="."
SKILLS=""
DRY_RUN=0
CHECK=0
FORCE=0
PRUNE=0

usage() {
  cat <<'EOF'
Usage: install.sh [options]

Install Agent Skills adapters from a GitHub archive without cloning.

Options:
  --target <cursor|copilot|augment|all>   Target IDE adapters (default: all)
  --invocation <auto|manual|both>         Invocation mode (default: both)
  --workspace <path>                      Target workspace path (default: .)
  --skills <csv>                          Optional comma-separated skill names
  --ref <git-ref>                         Branch/tag/commit ref (default: master)
  --repo <owner/name>                     GitHub repository (default: vegeta03/agent-skills)
  --dry-run                               Show planned writes only
  --check                                 Drift check mode (non-zero on drift)
  --force                                 Overwrite non-generated conflicts
  --prune                                 Remove stale generated files
  -h, --help                              Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"; shift 2 ;;
    --invocation)
      INVOCATION="${2:-}"; shift 2 ;;
    --workspace)
      WORKSPACE="${2:-}"; shift 2 ;;
    --skills)
      SKILLS="${2:-}"; shift 2 ;;
    --ref)
      REF="${2:-}"; shift 2 ;;
    --repo)
      REPO="${2:-}"; shift 2 ;;
    --dry-run)
      DRY_RUN=1; shift ;;
    --check)
      CHECK=1; shift ;;
    --force)
      FORCE=1; shift ;;
    --prune)
      PRUNE=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2 ;;
  esac
done

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Python is required but was not found." >&2
  exit 1
fi

if command -v curl >/dev/null 2>&1; then
  DOWNLOAD_CMD="curl"
elif command -v wget >/dev/null 2>&1; then
  DOWNLOAD_CMD="wget"
else
  echo "curl or wget is required to download the archive." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

ARCHIVE_PATH="$TMP_DIR/repo.tar.gz"
ARCHIVE_URL="https://github.com/${REPO}/archive/${REF}.tar.gz"

echo "Downloading ${ARCHIVE_URL}"
if [[ "$DOWNLOAD_CMD" == "curl" ]]; then
  curl -fsSL "$ARCHIVE_URL" -o "$ARCHIVE_PATH"
else
  wget -qO "$ARCHIVE_PATH" "$ARCHIVE_URL"
fi

tar -xzf "$ARCHIVE_PATH" -C "$TMP_DIR"
EXTRACTED_DIR="$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
if [[ -z "${EXTRACTED_DIR}" ]]; then
  echo "Failed to extract repository archive." >&2
  exit 1
fi

SYNC_SCRIPT="$EXTRACTED_DIR/scripts/sync.py"
if [[ ! -f "$SYNC_SCRIPT" ]]; then
  echo "sync.py not found in downloaded archive." >&2
  exit 1
fi

SYNC_ARGS=(
  "$SYNC_SCRIPT"
  "--target" "$TARGET"
  "--invocation" "$INVOCATION"
  "--workspace" "$WORKSPACE"
)

if [[ -n "$SKILLS" ]]; then
  SYNC_ARGS+=("--skills" "$SKILLS")
fi
if [[ "$DRY_RUN" -eq 1 ]]; then
  SYNC_ARGS+=("--dry-run")
fi
if [[ "$CHECK" -eq 1 ]]; then
  SYNC_ARGS+=("--check")
fi
if [[ "$FORCE" -eq 1 ]]; then
  SYNC_ARGS+=("--force")
fi
if [[ "$PRUNE" -eq 1 ]]; then
  SYNC_ARGS+=("--prune")
fi

"$PYTHON_BIN" "${SYNC_ARGS[@]}"
