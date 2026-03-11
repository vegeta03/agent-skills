#!/usr/bin/env python3
"""
Improve a skill description by calling an AI model CLI.

Takes:
  - The current description
  - A list of eval results (query, should_trigger, actually_triggered)
  - The skill name and path

Produces:
  - An improved description

## AI CLI Configuration

This script invokes an AI model via CLI subprocess. Configure via environment variables:

  AI_CLI_COMMAND   - The CLI command to invoke the AI model.
                     Default: auto-detects from available CLIs (claude, aider, etc.)
                     Examples:
                       "claude -p"           (Claude Code CLI)
                       "aider --message"     (Aider CLI)
                       "sgpt"               (Shell GPT)
                       "llm"                (Simon Willison's llm tool)
                     The command must accept a prompt on stdin/as argument and
                     return text on stdout. The script pipes the prompt via stdin.

  AI_CLI_FLAGS     - Additional flags to pass to the CLI (optional).
                     Default: ""
                     Examples:
                       "--model gpt-4"
                       "--output-format json"

Usage:
    python -m scripts.improve_description \\
      --skill-name my-skill \\
      --skill-path /path/to/my-skill \\
      --current-description "Current description text" \\
      --eval-results /path/to/eval_results.json
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _detect_ai_cli() -> list[str]:
    """Auto-detect an available AI CLI tool.

    Returns a list of command parts (e.g., ["claude", "-p"]).
    """
    candidates = [
        (["claude", "-p"], "Claude Code CLI"),
        (["aider", "--message"], "Aider CLI"),
        (["sgpt"], "Shell GPT"),
        (["llm"], "llm CLI"),
    ]

    for cmd_parts, name in candidates:
        if shutil.which(cmd_parts[0]):
            print(f"  Auto-detected AI CLI: {name} ({cmd_parts[0]})", file=sys.stderr)
            return cmd_parts

    print(
        "  ERROR: No AI CLI found. Set AI_CLI_COMMAND environment variable.\n"
        "  Supported CLIs: claude, aider, sgpt, llm\n"
        "  Example: export AI_CLI_COMMAND='claude -p'",
        file=sys.stderr,
    )
    sys.exit(1)


def _get_ai_cli() -> list[str]:
    """Get the AI CLI command from environment or auto-detect."""
    env_cmd = os.environ.get("AI_CLI_COMMAND", "").strip()
    if env_cmd:
        parts = env_cmd.split()
        extra_flags = os.environ.get("AI_CLI_FLAGS", "").strip()
        if extra_flags:
            parts.extend(extra_flags.split())
        return parts
    return _detect_ai_cli()


def _call_ai_cli(prompt: str) -> str:
    """Call the AI CLI with a prompt and return the response text."""
    cmd = _get_ai_cli()

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"  AI CLI error (exit {result.returncode}):", file=sys.stderr)
            print(f"  stderr: {result.stderr[:500]}", file=sys.stderr)
            return ""
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("  AI CLI timed out after 120s", file=sys.stderr)
        return ""
    except FileNotFoundError:
        print(f"  AI CLI command not found: {cmd[0]}", file=sys.stderr)
        print("  Set AI_CLI_COMMAND environment variable.", file=sys.stderr)
        return ""


def build_improvement_prompt(
    skill_name: str,
    current_description: str,
    eval_results: list[dict],
    skill_body: str = "",
) -> str:
    """Build the prompt for the AI to improve the skill description."""

    # Separate results into categories
    false_negatives = [r for r in eval_results if r["should_trigger"] and not r["triggered"]]
    false_positives = [r for r in eval_results if not r["should_trigger"] and r["triggered"]]
    correct = [r for r in eval_results if r["should_trigger"] == r["triggered"]]

    prompt = f"""You are a skill description optimizer. Your job is to improve the triggering
description for a skill so that it activates on the right queries and stays silent on the wrong ones.

## Current Description

{current_description}

## Skill Name

{skill_name}

## Skill Body (for context)

{skill_body[:3000] if skill_body else "(not provided)"}

## Eval Results

### Correct ({len(correct)})
"""
    for r in correct:
        status = "✓ triggered" if r["triggered"] else "✓ not triggered"
        prompt += f"- [{status}] {r['query']}\n"

    prompt += f"\n### False Negatives - should have triggered but didn't ({len(false_negatives)})\n"
    for r in false_negatives:
        prompt += f"- {r['query']}\n"

    prompt += f"\n### False Positives - triggered but shouldn't have ({len(false_positives)})\n"
    for r in false_positives:
        prompt += f"- {r['query']}\n"

    prompt += """
## Instructions

Study the false negatives and false positives carefully. Then write an improved description that:
1. Covers the concepts from the false negatives (so they'd trigger next time)
2. Excludes or narrows away from the false positive patterns
3. Keeps the description concise (under 1024 characters)
4. Maintains all existing correct triggers

The description field is the primary triggering mechanism - it determines whether the AI assistant
invokes this skill. Include both what the skill does AND specific contexts for when to use it.

Be a bit "pushy" - mention specific scenarios and keywords that should trigger this skill,
even if the user doesn't explicitly ask for it. AI assistants tend to "undertrigger" skills,
so erring on the side of triggering more often is better.

Return ONLY the improved description text wrapped in <new_description> tags:

<new_description>
Your improved description here
</new_description>
"""
    return prompt


def extract_description(response: str) -> str | None:
    """Extract the description from <new_description> tags."""
    match = re.search(r"<new_description>\s*(.*?)\s*</new_description>", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def main():
    parser = argparse.ArgumentParser(description="Improve a skill description using AI")
    parser.add_argument("--skill-name", required=True, help="Name of the skill")
    parser.add_argument("--skill-path", required=True, type=Path, help="Path to skill directory")
    parser.add_argument(
        "--current-description", required=True, help="Current description text"
    )
    parser.add_argument(
        "--eval-results", required=True, type=Path, help="Path to eval results JSON"
    )
    parser.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Output file for the improved description (default: stdout)"
    )
    args = parser.parse_args()

    # Load eval results
    try:
        eval_results = json.loads(args.eval_results.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading eval results: {e}", file=sys.stderr)
        sys.exit(1)

    # Read skill body for context
    skill_body = ""
    skill_md = args.skill_path / "SKILL.md"
    if skill_md.exists():
        try:
            skill_body = skill_md.read_text()
        except OSError:
            pass

    # Build and send the prompt
    prompt = build_improvement_prompt(
        args.skill_name, args.current_description, eval_results, skill_body
    )

    print("  Calling AI CLI for description improvement...", file=sys.stderr)
    response = _call_ai_cli(prompt)

    if not response:
        print("  ERROR: No response from AI CLI", file=sys.stderr)
        sys.exit(1)

    new_description = extract_description(response)
    if not new_description:
        print("  WARNING: Could not extract description from response", file=sys.stderr)
        print("  Raw response:", file=sys.stderr)
        print(response[:2000], file=sys.stderr)
        sys.exit(1)

    # Output result
    result = {
        "previous_description": args.current_description,
        "new_description": new_description,
        "eval_summary": {
            "total": len(eval_results),
            "correct": sum(1 for r in eval_results if r["should_trigger"] == r["triggered"]),
            "false_negatives": sum(
                1 for r in eval_results if r["should_trigger"] and not r["triggered"]
            ),
            "false_positives": sum(
                1 for r in eval_results if not r["should_trigger"] and r["triggered"]
            ),
        },
    }

    output_text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_text + "\n")
        print(f"  Result written to: {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
