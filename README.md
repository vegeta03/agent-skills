# Agent Skills

A collection of AI coding assistant skills that work with **any IDE** (Cursor, Windsurf, Cline, Aider, JetBrains AI, GitHub Copilot, etc.) and **any AI model** (Claude, GPT-4, Gemini, Llama, Mistral, etc.).

Skills are structured instruction sets that teach AI assistants how to perform specialized tasks — from code review to document generation to generative art.

## Quick Install

Install all skills for all supported IDEs with a single command:

**Bash (macOS / Linux):**
```bash
curl -fsSL "https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.sh" | bash -s -- --target all --invocation both --workspace .
```

**PowerShell (Windows):**
```powershell
iex "& { $(irm https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.ps1) } -Target all -Invocation both -Workspace ."
```

## Available Skills

| Skill | Description |
|-------|-------------|
| **algorithmic-art** | Create generative art using p5.js with seeded randomness and interactive parameter exploration |
| **code-review** | Automated code review for pull requests using multiple specialized agents with confidence-based scoring |
| **doc-coauthoring** | Structured workflow for co-authoring documentation, proposals, technical specs, and decision docs |
| **docx** | Create, read, edit, and manipulate Word documents (.docx files) with full formatting support |
| **explanatory-output-style** | Educational insights mode providing codebase-specific explanations about implementation choices and patterns |
| **feature-dev** | Comprehensive 7-phase feature development workflow with specialized agents for exploration, architecture, and review |
| **frontend-design** | Create distinctive, production-grade frontend interfaces with high design quality |
| **internal-comms** | Write internal communications — status reports, leadership updates, newsletters, FAQs, incident reports |
| **learning-output-style** | Interactive learning mode with hands-on coding guidance and educational explanations |
| **mcp-builder** | Guide for creating MCP (Model Context Protocol) servers for LLM integration with external services |
| **pdf** | Read, create, edit, merge, split, fill forms, OCR, and manipulate PDF files |
| **pptx** | Create, read, edit, and manipulate PowerPoint presentations (.pptx files) |
| **ralph-wiggum** | Iterative, self-referential AI development loops — run the AI in a while-true loop until task completion |
| **skill-creator** | Create new skills, modify existing skills, measure performance with evals, and optimize descriptions |
| **web-artifacts-builder** | Build elaborate, multi-component self-contained HTML artifacts using React, Tailwind CSS, and shadcn/ui |
| **webapp-testing** | Test local web applications using Playwright — verify frontend functionality, capture screenshots, view logs |
| **xlsx** | Create, read, edit, and manipulate spreadsheet files (.xlsx, .xlsm, .csv, .tsv) |

## Installation Options

### Install Specific Skills

**Bash:**
```bash
curl -fsSL "https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.sh" | \
  bash -s -- --target cursor --skills code-review,feature-dev --workspace .
```

**PowerShell:**
```powershell
$u="https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.ps1"
$f=Join-Path $env:TEMP "agent-skills-install.ps1"; iwr $u -OutFile $f
& $f -Target cursor -Skills "code-review,feature-dev" -Workspace .
```

### Install for a Specific IDE

```bash
# GitHub Copilot only
curl -fsSL "https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.sh" | \
  bash -s -- --target copilot --invocation manual --skills skill-creator --workspace .

# Cursor only
curl -fsSL "https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.sh" | \
  bash -s -- --target cursor --invocation both --workspace .
```

### Parameters

| Parameter | Bash | PowerShell | Values | Default |
|-----------|------|------------|--------|---------|
| Target IDE | `--target` | `-Target` | `all`, `cursor`, `windsurf`, `cline`, `aider`, `copilot`, `jetbrains` | `all` |
| Invocation mode | `--invocation` | `-Invocation` | `both`, `manual`, `automatic` | `both` |
| Skills | `--skills` | `-Skills` | Comma-separated names or `all` | `all` |
| Workspace path | `--workspace` | `-Workspace` | Directory path | `.` |

### Invocation Modes

- **manual** — Skill is available but the user must explicitly invoke it (e.g., "use the code-review skill")
- **automatic** — Skill is always loaded into context and triggers based on its description
- **both** — Installs both manual and automatic configurations

## IDE Installation Paths

Each IDE stores skill/instruction files in a specific location:

| IDE | Directory | File Format | Notes |
|-----|-----------|-------------|-------|
| **Cursor** | `.cursor/rules/` | `*.mdc` | Uses `alwaysApply: true/false` in frontmatter |
| **Windsurf** | `.windsurfrules/` | `*.md` | Plain markdown files |
| **Cline** | `.clinerules/` | `*.md` | Plain markdown files |
| **Aider** | `.aider/` | `*.md` | Convention-based files |
| **GitHub Copilot** | `.github/instructions/` | `*.instructions.md` | Uses `applyTo` in frontmatter |
| **JetBrains AI** | `.junie/` | `*.md` | Guideline markdown files |

## Skill Structure

Each skill follows a standard structure:

```
skill-name/
├── SKILL.md              # Main skill instructions (required)
├── LICENSE.txt            # License terms (if applicable)
├── scripts/              # Helper scripts for deterministic tasks
├── references/           # Documentation loaded as needed
├── agents/               # Sub-agent instruction files
├── templates/            # Template files for output
└── examples/             # Example files and patterns
```

The installer downloads `SKILL.md` and converts it to the appropriate IDE format. Bundled resources (scripts, references, templates, etc.) are placed in a `<skill-name>-resources/` subdirectory.

## Advanced Usage

### Download and Execute (Bash)

If you prefer to inspect the script before running:

```bash
curl -fsSL "https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.sh" -o "/tmp/agent-skills-install.sh"
cat /tmp/agent-skills-install.sh   # inspect
bash "/tmp/agent-skills-install.sh" --target all --invocation both --workspace .
```

### Download and Execute (PowerShell)

```powershell
$u = "https://raw.githubusercontent.com/vegeta03/agent-skills/master/scripts/install.ps1"
$f = Join-Path $env:TEMP "agent-skills-install.ps1"
iwr $u -OutFile $f
Get-Content $f   # inspect
& $f -Target all -Invocation both -Workspace .
```

### Idempotent

Both scripts are safe to run multiple times. They will overwrite existing skill files with the latest versions from the repository.

## Contributing

Each skill lives in its own top-level directory. To add a new skill:

1. Create a directory with your skill name (e.g., `my-skill/`)
2. Add a `SKILL.md` with YAML frontmatter (`name` and `description` fields are required)
3. Add any bundled resources in subdirectories (`scripts/`, `references/`, etc.)
4. Update the `ALL_SKILLS` array and `SKILL_FILES` manifest in both `scripts/install.sh` and `scripts/install.ps1`

## License

Individual skills may have their own licenses — check each skill's `LICENSE.txt` file. Skills without a `LICENSE.txt` are provided as-is.

