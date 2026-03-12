<#
.SYNOPSIS
    Agent Skills Installer (PowerShell)
    Install AI coding assistant skills without cloning the entire repository.
.DESCRIPTION
    Works with: Cursor, Windsurf, Cline, Aider, JetBrains AI, GitHub Copilot, etc.
.PARAMETER Target
    Target IDE: all, cursor, windsurf, cline, aider, copilot, jetbrains (default: all)
.PARAMETER Invocation
    Invocation mode: both, manual, automatic (default: both)
.PARAMETER Skills
    Comma-separated skill names or "all" (default: all)
.PARAMETER Workspace
    Workspace root directory (default: current directory)
.EXAMPLE
    .\install.ps1 -Target all -Invocation both -Workspace .
.EXAMPLE
    .\install.ps1 -Target cursor -Skills "code-review,feature-dev" -Workspace C:\project
#>
param(
    [ValidateSet("all","cursor","windsurf","cline","aider","copilot","jetbrains")]
    [string]$Target = "all",

    [ValidateSet("both","manual","automatic")]
    [string]$Invocation = "both",

    [string]$Skills = "all",

    [string]$Workspace = "."
)

$ErrorActionPreference = "Stop"

$RepoRawBase = "https://raw.githubusercontent.com/vegeta03/agent-skills/master"

$AllSkills = @(
    "algorithmic-art"
    "code-review"
    "doc-coauthoring"
    "docx"
    "explanatory-output-style"
    "feature-dev"
    "frontend-design"
    "internal-comms"
    "learning-output-style"
    "mcp-builder"
    "pdf"
    "pptx"
    "ralph-wiggum"
    "skill-creator"
    "web-artifacts-builder"
    "webapp-testing"
    "xlsx"
)

# Skill file manifests (extra files beyond SKILL.md)
$SkillFiles = @{
    "algorithmic-art"        = @("templates/viewer.html","templates/generator_template.js","LICENSE.txt")
    "code-review"            = @()
    "doc-coauthoring"        = @()
    "explanatory-output-style" = @()
    "feature-dev"            = @("agents/code-explorer.md","agents/code-architect.md","agents/code-reviewer.md")
    "frontend-design"        = @()
    "internal-comms"         = @("examples/3p-updates.md","examples/company-newsletter.md","examples/faq-answers.md","examples/general-comms.md","LICENSE.txt")
    "learning-output-style"  = @()
    "mcp-builder"            = @("reference/evaluation.md","reference/mcp_best_practices.md","reference/node_mcp_server.md","reference/python_mcp_server.md","scripts/connections.py","scripts/evaluation.py","scripts/example_evaluation.xml","scripts/requirements.txt","LICENSE.txt")
    "ralph-wiggum"           = @("scripts/setup-ralph-loop.sh","scripts/stop-hook.sh")
    "skill-creator"          = @("agents/analyzer.md","agents/comparator.md","agents/grader.md","assets/eval_review.html","eval-viewer/generate_review.py","eval-viewer/viewer.html","references/schemas.md","scripts/__init__.py","scripts/aggregate_benchmark.py","scripts/generate_report.py","scripts/improve_description.py","scripts/package_skill.py","scripts/quick_validate.py","scripts/run_eval.py","scripts/run_loop.py","scripts/utils.py","LICENSE.txt")
    "web-artifacts-builder"  = @("scripts/bundle-artifact.sh","scripts/init-artifact.sh","scripts/shadcn-components.tar.gz","LICENSE.txt")
    "webapp-testing"         = @("examples/console_logging.py","examples/element_discovery.py","examples/static_html_automation.py","scripts/with_server.py","LICENSE.txt")
    "docx"                   = @("scripts/__init__.py","scripts/accept_changes.py","scripts/comment.py","scripts/office/soffice.py","scripts/office/unpack.py","scripts/office/pack.py","scripts/office/validate.py","scripts/office/helpers/__init__.py","scripts/office/helpers/merge_runs.py","scripts/office/helpers/simplify_redlines.py","scripts/office/validators/__init__.py","scripts/office/validators/base.py","scripts/office/validators/docx.py","scripts/office/validators/pptx.py","scripts/office/validators/redlining.py","scripts/templates/comments.xml","scripts/templates/commentsExtended.xml","scripts/templates/commentsExtensible.xml","scripts/templates/commentsIds.xml","scripts/templates/people.xml","LICENSE.txt")
    "pdf"                    = @("forms.md","reference.md","scripts/check_bounding_boxes.py","scripts/check_fillable_fields.py","scripts/convert_pdf_to_images.py","scripts/create_validation_image.py","scripts/extract_form_field_info.py","scripts/extract_form_structure.py","scripts/fill_fillable_fields.py","scripts/fill_pdf_form_with_annotations.py","LICENSE.txt")
    "pptx"                   = @("editing.md","pptxgenjs.md","scripts/__init__.py","scripts/add_slide.py","scripts/clean.py","scripts/thumbnail.py","scripts/office/soffice.py","scripts/office/unpack.py","scripts/office/pack.py","scripts/office/validate.py","scripts/office/helpers/__init__.py","scripts/office/helpers/merge_runs.py","scripts/office/helpers/simplify_redlines.py","scripts/office/validators/__init__.py","scripts/office/validators/base.py","scripts/office/validators/docx.py","scripts/office/validators/pptx.py","scripts/office/validators/redlining.py","LICENSE.txt")
    "xlsx"                   = @("scripts/recalc.py","scripts/office/soffice.py","scripts/office/unpack.py","scripts/office/pack.py","scripts/office/validate.py","scripts/office/helpers/__init__.py","scripts/office/helpers/merge_runs.py","scripts/office/helpers/simplify_redlines.py","scripts/office/validators/__init__.py","scripts/office/validators/base.py","scripts/office/validators/docx.py","scripts/office/validators/pptx.py","scripts/office/validators/redlining.py","LICENSE.txt")
}

# Resolve workspace path
$Workspace = (Resolve-Path $Workspace).Path

# Resolve skill list
if ($Skills -eq "all") {
    $SkillList = $AllSkills
} else {
    $SkillList = $Skills -split ","
}

# Validate skill names
foreach ($s in $SkillList) {
    if ($s -notin $AllSkills) {
        Write-Error "Unknown skill '$s'. Available: $($AllSkills -join ', ')"
        exit 1
    }
}

Write-Host "==================================================================="
Write-Host " Agent Skills Installer"
Write-Host "==================================================================="
Write-Host " Target:     $Target"
Write-Host " Invocation: $Invocation"
Write-Host " Skills:     $($SkillList -join ', ')"
Write-Host " Workspace:  $Workspace"
Write-Host "==================================================================="
Write-Host ""

# ── IDE directory mapping ────────────────────────────────────────────────────
function Get-IdeDir {
    param([string]$Ide)
    switch ($Ide) {
        "cursor"    { return ".cursor\rules" }
        "windsurf"  { return ".windsurfrules" }
        "cline"     { return ".clinerules" }
        "aider"     { return ".aider" }
        "copilot"   { return ".github\instructions" }
        "jetbrains" { return ".junie" }
    }
}

# ── Download a file from GitHub ──────────────────────────────────────────────
function Download-File {
    param([string]$Url, [string]$Dest)
    $dir = Split-Path $Dest -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    try {
        Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# ── Install a skill for a specific IDE ───────────────────────────────────────
function Install-Skill {
    param([string]$Skill, [string]$Ide, [string]$Mode)

    $ideDir = Get-IdeDir $Ide
    $destBase = Join-Path $Workspace $ideDir

    # Determine output filename per IDE
    switch ($Ide) {
        "cursor"    { $skillFile = "$Skill.mdc" }
        "copilot"   { $skillFile = "$Skill.instructions.md" }
        default     { $skillFile = "$Skill.md" }
    }
    $skillDest = Join-Path $destBase $skillFile

    # Download SKILL.md to temp
    $rawUrl = "$RepoRawBase/$Skill/SKILL.md"
    $tmpFile = Join-Path $env:TEMP "agent-skill-$Skill.md"
    $ok = Download-File $rawUrl $tmpFile
    if (-not $ok) {
        Write-Warning "  ✗ Failed to download $Skill"
        return
    }

    $content = Get-Content $tmpFile -Raw
    # Extract description from frontmatter
    $description = ""
    if ($content -match '(?ms)^---\s*\n(.*?)\n---') {
        $fm = $Matches[1]
        if ($fm -match '(?m)^description:\s*"?(.+?)"?\s*$') {
            $description = $Matches[1]
        }
    }
    # Extract body after second ---
    $parts = $content -split '(?m)^---\s*$', 3
    $body = if ($parts.Count -ge 3) { $parts[2].TrimStart("`n`r") } else { $content }

    if (-not (Test-Path $destBase)) { New-Item -ItemType Directory -Path $destBase -Force | Out-Null }

    switch ($Ide) {
        "cursor" {
            $alwaysApply = if ($Mode -eq "automatic") { "true" } else { "false" }
            $output = "---`ndescription: $description`nalwaysApply: $alwaysApply`n---`n`n$body"
            Set-Content -Path $skillDest -Value $output -Encoding UTF8
        }
        "copilot" {
            $output = "---`napplyTo: '**'`n---`n`n$body"
            Set-Content -Path $skillDest -Value $output -Encoding UTF8
        }
        default {
            Set-Content -Path $skillDest -Value $body -Encoding UTF8
        }
    }
    Write-Host "  $(([char]0x2713)) $Skill -> $ideDir\$skillFile"

    # Download bundled resource files
    $extras = $SkillFiles[$Skill]
    if ($extras -and $extras.Count -gt 0) {
        $resDir = Join-Path $destBase "$Skill-resources"
        foreach ($f in $extras) {
            $fUrl = "$RepoRawBase/$Skill/$f"
            $fDest = Join-Path $resDir ($f -replace '/', '\')
            if (Download-File $fUrl $fDest) {
                Write-Host "    + $f"
            }
        }
    }

    Remove-Item $tmpFile -ErrorAction SilentlyContinue
}

# ── Determine targets ────────────────────────────────────────────────────────
$Targets = if ($Target -eq "all") {
    @("cursor","windsurf","cline","aider","copilot","jetbrains")
} else {
    @($Target)
}

$Modes = if ($Invocation -eq "both") {
    @("manual","automatic")
} else {
    @($Invocation)
}

# ── Main installation loop ───────────────────────────────────────────────────
$total = 0
foreach ($ide in $Targets) {
    foreach ($mode in $Modes) {
        Write-Host "Installing for $ide ($mode invocation)..."
        foreach ($skill in $SkillList) {
            Install-Skill -Skill $skill -Ide $ide -Mode $mode
            $total++
        }
        Write-Host ""
    }
}

Write-Host "==================================================================="
Write-Host " Installation complete!"
Write-Host " Installed $total skill configuration(s)."
Write-Host "==================================================================="
Write-Host ""
Write-Host "Tip: Restart your IDE to pick up the new skill files."

