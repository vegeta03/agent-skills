#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Agent Skills Installer (Bash)
# Install AI coding assistant skills without cloning the entire repository.
# Works with: Cursor, Windsurf, Cline, Aider, JetBrains AI, GitHub Copilot, etc.
# ─────────────────────────────────────────────────────────────────────────────

REPO_RAW_BASE="https://raw.githubusercontent.com/vegeta03/agent-skills/master"

ALL_SKILLS=(
  algorithmic-art
  code-review
  doc-coauthoring
  docx
  explanatory-output-style
  feature-dev
  frontend-design
  internal-comms
  learning-output-style
  mcp-builder
  pdf
  pptx
  ralph-wiggum
  skill-creator
  web-artifacts-builder
  webapp-testing
  xlsx
)

# ── Skill file manifests (files beyond SKILL.md) ────────────────────────────
# Each key lists extra files that belong to a skill directory.
declare -A SKILL_FILES
SKILL_FILES[algorithmic-art]="templates/viewer.html templates/generator_template.js LICENSE.txt"
SKILL_FILES[code-review]=""
SKILL_FILES[doc-coauthoring]=""
SKILL_FILES[explanatory-output-style]=""
SKILL_FILES[feature-dev]="agents/code-explorer.md agents/code-architect.md agents/code-reviewer.md"
SKILL_FILES[frontend-design]=""
SKILL_FILES[internal-comms]="examples/3p-updates.md examples/company-newsletter.md examples/faq-answers.md examples/general-comms.md LICENSE.txt"
SKILL_FILES[learning-output-style]=""
SKILL_FILES[mcp-builder]="reference/evaluation.md reference/mcp_best_practices.md reference/node_mcp_server.md reference/python_mcp_server.md scripts/connections.py scripts/evaluation.py scripts/example_evaluation.xml scripts/requirements.txt LICENSE.txt"
SKILL_FILES[ralph-wiggum]="scripts/setup-ralph-loop.sh scripts/stop-hook.sh"
SKILL_FILES[skill-creator]="agents/analyzer.md agents/comparator.md agents/grader.md assets/eval_review.html eval-viewer/generate_review.py eval-viewer/viewer.html references/schemas.md scripts/__init__.py scripts/aggregate_benchmark.py scripts/generate_report.py scripts/improve_description.py scripts/package_skill.py scripts/quick_validate.py scripts/run_eval.py scripts/run_loop.py scripts/utils.py LICENSE.txt"
SKILL_FILES[web-artifacts-builder]="scripts/bundle-artifact.sh scripts/init-artifact.sh scripts/shadcn-components.tar.gz LICENSE.txt"
SKILL_FILES[webapp-testing]="examples/console_logging.py examples/element_discovery.py examples/static_html_automation.py scripts/with_server.py LICENSE.txt"
SKILL_FILES[docx]="scripts/__init__.py scripts/accept_changes.py scripts/comment.py scripts/office/soffice.py scripts/office/unpack.py scripts/office/pack.py scripts/office/validate.py scripts/office/helpers/__init__.py scripts/office/helpers/merge_runs.py scripts/office/helpers/simplify_redlines.py scripts/office/validators/__init__.py scripts/office/validators/base.py scripts/office/validators/docx.py scripts/office/validators/pptx.py scripts/office/validators/redlining.py scripts/templates/comments.xml scripts/templates/commentsExtended.xml scripts/templates/commentsExtensible.xml scripts/templates/commentsIds.xml scripts/templates/people.xml LICENSE.txt"
SKILL_FILES[pdf]="forms.md reference.md scripts/check_bounding_boxes.py scripts/check_fillable_fields.py scripts/convert_pdf_to_images.py scripts/create_validation_image.py scripts/extract_form_field_info.py scripts/extract_form_structure.py scripts/fill_fillable_fields.py scripts/fill_pdf_form_with_annotations.py LICENSE.txt"
SKILL_FILES[pptx]="editing.md pptxgenjs.md scripts/__init__.py scripts/add_slide.py scripts/clean.py scripts/thumbnail.py scripts/office/soffice.py scripts/office/unpack.py scripts/office/pack.py scripts/office/validate.py scripts/office/helpers/__init__.py scripts/office/helpers/merge_runs.py scripts/office/helpers/simplify_redlines.py scripts/office/validators/__init__.py scripts/office/validators/base.py scripts/office/validators/docx.py scripts/office/validators/pptx.py scripts/office/validators/redlining.py LICENSE.txt"
SKILL_FILES[xlsx]="scripts/recalc.py scripts/office/soffice.py scripts/office/unpack.py scripts/office/pack.py scripts/office/validate.py scripts/office/helpers/__init__.py scripts/office/helpers/merge_runs.py scripts/office/helpers/simplify_redlines.py scripts/office/validators/__init__.py scripts/office/validators/base.py scripts/office/validators/docx.py scripts/office/validators/pptx.py scripts/office/validators/redlining.py LICENSE.txt"

# ── Defaults ─────────────────────────────────────────────────────────────────
TARGET="all"
INVOCATION="both"
SKILLS_ARG="all"
WORKSPACE="."

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install Agent Skills for AI coding assistants.

Options:
  --target <ide>        Target IDE: all, cursor, windsurf, cline, aider, copilot, jetbrains
                        (default: all)
  --invocation <mode>   Invocation mode: both, manual, automatic (default: both)
  --skills <names>      Comma-separated skill names or "all" (default: all)
  --workspace <path>    Workspace root directory (default: current directory)
  -h, --help            Show this help message

Examples:
  $(basename "$0") --target all --invocation both --workspace .
  $(basename "$0") --target cursor --skills code-review,feature-dev --workspace ~/project
  $(basename "$0") --target copilot --invocation manual --skills skill-creator
EOF
  exit 0
}

# ── Parse arguments ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)    TARGET="$2";     shift 2 ;;
    --invocation) INVOCATION="$2"; shift 2 ;;
    --skills)    SKILLS_ARG="$2";  shift 2 ;;
    --workspace) WORKSPACE="$2";   shift 2 ;;
    -h|--help)   usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

# Resolve workspace to absolute path
WORKSPACE="$(cd "$WORKSPACE" 2>/dev/null && pwd)"

# ── Validate arguments ───────────────────────────────────────────────────────
VALID_TARGETS="all cursor windsurf cline aider copilot jetbrains"
if ! echo "$VALID_TARGETS" | grep -qw "$TARGET"; then
  echo "Error: Invalid target '$TARGET'. Must be one of: $VALID_TARGETS" >&2; exit 1
fi

VALID_INVOCATIONS="both manual automatic"
if ! echo "$VALID_INVOCATIONS" | grep -qw "$INVOCATION"; then
  echo "Error: Invalid invocation '$INVOCATION'. Must be one of: $VALID_INVOCATIONS" >&2; exit 1
fi

# ── Resolve skill list ───────────────────────────────────────────────────────
if [[ "$SKILLS_ARG" == "all" ]]; then
  SKILLS=("${ALL_SKILLS[@]}")
else
  IFS=',' read -ra SKILLS <<< "$SKILLS_ARG"
fi

# Validate skill names
for skill in "${SKILLS[@]}"; do
  found=0
  for valid in "${ALL_SKILLS[@]}"; do
    [[ "$skill" == "$valid" ]] && found=1 && break
  done
  if [[ $found -eq 0 ]]; then
    echo "Error: Unknown skill '$skill'." >&2
    echo "Available skills: ${ALL_SKILLS[*]}" >&2; exit 1
  fi
done

echo "═══════════════════════════════════════════════════════════════"
echo " Agent Skills Installer"
echo "═══════════════════════════════════════════════════════════════"
echo " Target:     $TARGET"
echo " Invocation: $INVOCATION"
echo " Skills:     ${SKILLS[*]}"
echo " Workspace:  $WORKSPACE"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ── IDE target directories ───────────────────────────────────────────────────
# Each IDE stores rules/skills in a specific location relative to the workspace.
# "manual" = user explicitly invokes; "automatic" = always loaded into context.
get_ide_dirs() {
  local ide="$1" mode="$2"
  case "$ide" in
    cursor)
      # Cursor uses .cursor/rules/ with .mdc files; alwaysApply=true for automatic
      echo ".cursor/rules"
      ;;
    windsurf)
      echo ".windsurfrules"
      ;;
    cline)
      echo ".clinerules"
      ;;
    aider)
      echo ".aider"
      ;;
    copilot)
      # GitHub Copilot uses .github/copilot-instructions.md (single file) or
      # .github/instructions/ directory for multiple instruction files
      echo ".github/instructions"
      ;;
    jetbrains)
      echo ".junie"
      ;;
  esac
}

# ── Download a single file from GitHub ───────────────────────────────────────
download_file() {
  local url="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if command -v curl &>/dev/null; then
    curl -fsSL "$url" -o "$dest" 2>/dev/null
  elif command -v wget &>/dev/null; then
    wget -q "$url" -O "$dest" 2>/dev/null
  else
    echo "Error: Neither curl nor wget found. Cannot download files." >&2; exit 1
  fi
}

# ── Install a skill to a specific IDE directory ──────────────────────────────
install_skill_for_ide() {
  local skill="$1" ide="$2" mode="$3"
  local ide_dir
  ide_dir="$(get_ide_dirs "$ide" "$mode")"
  local dest_base="$WORKSPACE/$ide_dir"

  # Determine skill file name and format per IDE
  local skill_file skill_dest
  case "$ide" in
    cursor)
      skill_file="${skill}.mdc"
      skill_dest="$dest_base/$skill_file"
      ;;
    windsurf|cline|aider|jetbrains)
      skill_file="${skill}.md"
      skill_dest="$dest_base/$skill_file"
      ;;
    copilot)
      skill_file="${skill}.instructions.md"
      skill_dest="$dest_base/$skill_file"
      ;;
  esac

  # Download the main SKILL.md
  local raw_url="$REPO_RAW_BASE/$skill/SKILL.md"
  local tmp_skill
  tmp_skill="$(mktemp)"
  download_file "$raw_url" "$tmp_skill"

  # Extract frontmatter description for IDE-specific formatting
  local description=""
  description="$(sed -n '/^---$/,/^---$/{ /^---$/d; /^description:/{ s/^description: *//; s/^"//; s/"$//; p; }; }' "$tmp_skill")"

  # Extract body (everything after the second ---)
  local body=""
  body="$(awk 'BEGIN{c=0} /^---$/{c++;next} c>=2{print}' "$tmp_skill")"

  mkdir -p "$dest_base"

  case "$ide" in
    cursor)
      # Cursor .mdc format with frontmatter
      local apply_mode="agent"
      if [[ "$mode" == "automatic" ]]; then
        apply_mode="always"
      fi
      {
        echo "---"
        echo "description: $description"
        echo "alwaysApply: $( [[ "$mode" == "automatic" ]] && echo "true" || echo "false" )"
        echo "---"
        echo ""
        echo "$body"
      } > "$skill_dest"
      ;;
    copilot)
      # GitHub Copilot .instructions.md format with YAML frontmatter
      {
        echo "---"
        echo "applyTo: '**'"
        echo "---"
        echo ""
        echo "$body"
      } > "$skill_dest"
      ;;
    *)
      # Windsurf, Cline, Aider, JetBrains — plain markdown
      {
        echo "$body"
      } > "$skill_dest"
      ;;
  esac

  echo "  ✓ $skill → $ide_dir/$( basename "$skill_dest" )"

  # Download bundled resource files into a subdirectory alongside the skill
  local extra_files="${SKILL_FILES[$skill]:-}"
  if [[ -n "$extra_files" ]]; then
    local res_dir="$dest_base/${skill}-resources"
    for f in $extra_files; do
      local f_url="$REPO_RAW_BASE/$skill/$f"
      local f_dest="$res_dir/$f"
      if download_file "$f_url" "$f_dest" 2>/dev/null; then
        echo "    + $f"
      fi
    done
  fi

  rm -f "$tmp_skill"
}

# ── Determine which IDEs to install for ──────────────────────────────────────
if [[ "$TARGET" == "all" ]]; then
  TARGETS=(cursor windsurf cline aider copilot jetbrains)
else
  TARGETS=("$TARGET")
fi

# Determine invocation modes
if [[ "$INVOCATION" == "both" ]]; then
  MODES=(manual automatic)
else
  MODES=("$INVOCATION")
fi

# ── Main installation loop ───────────────────────────────────────────────────
total=0
for ide in "${TARGETS[@]}"; do
  for mode in "${MODES[@]}"; do
    echo "Installing for $ide ($mode invocation)..."
    for skill in "${SKILLS[@]}"; do
      install_skill_for_ide "$skill" "$ide" "$mode"
      total=$((total + 1))
    done
    echo ""
  done
done

echo "═══════════════════════════════════════════════════════════════"
echo " Installation complete!"
echo " Installed $total skill configuration(s)."
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Tip: Restart your IDE to pick up the new skill files."

