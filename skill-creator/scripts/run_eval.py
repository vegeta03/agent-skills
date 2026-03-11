#!/usr/bin/env python3
"""
Run trigger evaluations for a skill description.

Tests whether an AI assistant correctly triggers (or doesn't trigger) a skill
for a set of evaluation queries.

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

  SKILL_TOOL_NAMES - Comma-separated names of tools that indicate skill triggering.
                     Default: "Skill,Read,read_file,view_file"
                     When the AI's response mentions using one of these tools with
                     the skill path, we count it as "triggered".

  SKILL_DIR        - Path to the directory containing skill files.
                     Default: current directory

Usage:
    python -m scripts.run_eval \\
      --eval-set /path/to/eval_set.json \\
      --skill-path /path/to/my-skill \\
      --model <model-id> \\
      --runs 3 \\
      --output /path/to/results.json
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def _detect_ai_cli() -> list[str]:
    """Auto-detect an available AI CLI tool."""
    candidates = [
        (["claude", "-p"], "Claude Code CLI"),
        (["aider", "--message"], "Aider CLI"),
        (["sgpt"], "Shell GPT"),
        (["llm"], "llm CLI"),
    ]

    for cmd_parts, name in candidates:
        if shutil.which(cmd_parts[0]):
            return cmd_parts

    print(
        "ERROR: No AI CLI found. Set AI_CLI_COMMAND environment variable.\n"
        "Supported CLIs: claude, aider, sgpt, llm\n"
        "Example: export AI_CLI_COMMAND='claude -p'",
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


def _get_skill_tool_names() -> list[str]:
    """Get the list of tool names that indicate skill triggering."""
    env_names = os.environ.get("SKILL_TOOL_NAMES", "").strip()
    if env_names:
        return [n.strip() for n in env_names.split(",") if n.strip()]
    return ["Skill", "Read", "read_file", "view_file", "cat", "open_file"]


def run_single_eval(
    query: str,
    skill_path: str,
    skill_name: str,
    description: str,
    model: str | None = None,
    timeout: int = 60,
) -> dict:
    """Run a single eval query and determine if the skill was triggered.

    Args:
        query: The user prompt to test
        skill_path: Path to the skill directory
        skill_name: Name of the skill
        description: Current skill description
        model: Model identifier (optional, appended as flag if provided)
        timeout: Timeout in seconds

    Returns:
        Dict with keys: query, triggered (bool), response, error (if any)
    """
    cmd = _get_ai_cli()

    # Add model flag if provided and the CLI supports it
    if model:
        # Only add --model if it's not already in the command
        cmd_str = " ".join(cmd)
        if "--model" not in cmd_str and "-m" not in cmd_str:
            cmd = cmd + ["--model", model]

    # Build a prompt that simulates having the skill available
    system_prompt = f"""You have access to a skill called "{skill_name}".
Description: {description}
Location: {skill_path}

If you think this skill is relevant to the user's request, indicate that you would
use/read/invoke it by mentioning the skill name and path. If the skill is not relevant,
just respond normally without mentioning it.

Respond with your plan for handling the request. If you would use the skill, say so explicitly.
"""

    full_prompt = f"{system_prompt}\n\nUser request: {query}"

    try:
        result = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        response = result.stdout.strip()
        error = result.stderr.strip() if result.returncode != 0 else None

        # Determine if skill was triggered
        triggered = _check_triggered(response, skill_name, skill_path)

        return {
            "query": query,
            "triggered": triggered,
            "response": response[:2000],  # Truncate for storage
            "error": error,
        }

    except subprocess.TimeoutExpired:
        return {
            "query": query,
            "triggered": False,
            "response": "",
            "error": f"Timeout after {timeout}s",
        }
    except FileNotFoundError:
        return {
            "query": query,
            "triggered": False,
            "response": "",
            "error": f"AI CLI not found: {cmd[0]}",
        }


def _check_triggered(response: str, skill_name: str, skill_path: str) -> bool:
    """Check if the response indicates the skill was triggered.

    Looks for mentions of skill-related tool names combined with
    the skill name or path.
    """
    response_lower = response.lower()
    skill_name_lower = skill_name.lower()
    skill_path_lower = skill_path.lower()

    # Check for explicit skill tool usage
    tool_names = _get_skill_tool_names()
    for tool_name in tool_names:
        if tool_name.lower() in response_lower:
            # Check if skill name or path is also mentioned nearby
            if skill_name_lower in response_lower or skill_path_lower in response_lower:
                return True

    # Check for direct mentions of using/invoking/reading the skill
    trigger_patterns = [
        rf"(?:use|invoke|read|consult|load|apply|activate)\s+.*{re.escape(skill_name_lower)}",
        rf"{re.escape(skill_name_lower)}\s+skill",
        rf"skill.*{re.escape(skill_name_lower)}",
        re.escape(skill_path_lower),
    ]

    for pattern in trigger_patterns:
        if re.search(pattern, response_lower):
            return True

    return False


def run_eval_set(
    eval_set: list[dict],
    skill_path: str,
    skill_name: str,
    description: str,
    model: str | None = None,
    runs: int = 1,
    max_workers: int = 4,
    timeout: int = 60,
    verbose: bool = False,
) -> list[dict]:
    """Run a full eval set, optionally multiple times.

    Args:
        eval_set: List of dicts with 'query' and 'should_trigger' keys
        skill_path: Path to the skill directory
        skill_name: Name of the skill
        description: Current skill description
        model: Model identifier (optional)
        runs: Number of runs per query
        max_workers: Max parallel workers
        timeout: Timeout per query
        verbose: Print progress

    Returns:
        List of result dicts with trigger rates
    """
    all_results = []

    for eval_item in eval_set:
        query = eval_item["query"]
        should_trigger = eval_item["should_trigger"]
        triggers = []

        if verbose:
            print(f"  Eval: {query[:80]}...", file=sys.stderr)

        # Run multiple times for reliability
        for run_num in range(runs):
            result = run_single_eval(
                query=query,
                skill_path=skill_path,
                skill_name=skill_name,
                description=description,
                model=model,
                timeout=timeout,
            )
            triggers.append(result["triggered"])

            if result.get("error"):
                if verbose:
                    print(f"    Run {run_num + 1}: ERROR - {result['error']}", file=sys.stderr)
            elif verbose:
                status = "triggered" if result["triggered"] else "not triggered"
                print(f"    Run {run_num + 1}: {status}", file=sys.stderr)

        trigger_rate = sum(triggers) / len(triggers) if triggers else 0.0
        correct = (trigger_rate >= 0.5) == should_trigger

        all_results.append({
            "query": query,
            "should_trigger": should_trigger,
            "triggered": trigger_rate >= 0.5,
            "trigger_rate": trigger_rate,
            "runs": runs,
            "correct": correct,
        })

        if verbose:
            symbol = "✓" if correct else "✗"
            print(
                f"    {symbol} trigger_rate={trigger_rate:.0%} "
                f"(should_trigger={should_trigger})",
                file=sys.stderr,
            )

    return all_results


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluations for a skill")
    parser.add_argument("--eval-set", required=True, type=Path, help="Path to eval set JSON")
    parser.add_argument("--skill-path", required=True, type=Path, help="Path to skill directory")
    parser.add_argument("--description", type=str, default=None, help="Override skill description")
    parser.add_argument("--model", type=str, default=None, help="Model identifier")
    parser.add_argument("--runs", type=int, default=3, help="Runs per query (default: 3)")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output file (default: stdout)")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per query in seconds")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print progress")
    args = parser.parse_args()

    # Load eval set
    try:
        eval_set = json.loads(args.eval_set.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading eval set: {e}", file=sys.stderr)
        sys.exit(1)

    # Get skill info
    skill_path = str(args.skill_path.resolve())
    try:
        from scripts.utils import parse_skill_md
        skill_name, default_desc, _ = parse_skill_md(args.skill_path)
    except Exception:
        skill_name = args.skill_path.name
        default_desc = ""

    description = args.description or default_desc
    if not description:
        print("Error: No skill description found. Use --description or fix SKILL.md.", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"  Skill: {skill_name}", file=sys.stderr)
        print(f"  Description: {description[:100]}...", file=sys.stderr)
        print(f"  Evals: {len(eval_set)}, Runs/eval: {args.runs}", file=sys.stderr)
        print(f"  Model: {args.model or '(default)'}", file=sys.stderr)
        print("", file=sys.stderr)

    # Run evals
    results = run_eval_set(
        eval_set=eval_set,
        skill_path=skill_path,
        skill_name=skill_name,
        description=description,
        model=args.model,
        runs=args.runs,
        timeout=args.timeout,
        verbose=args.verbose,
    )

    # Calculate summary
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    accuracy = correct / total if total else 0.0

    output = {
        "skill_name": skill_name,
        "description": description,
        "model": args.model,
        "runs_per_query": args.runs,
        "results": results,
        "summary": {
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "false_negatives": sum(
                1 for r in results if r["should_trigger"] and not r["triggered"]
            ),
            "false_positives": sum(
                1 for r in results if not r["should_trigger"] and r["triggered"]
            ),
        },
    }

    output_text = json.dumps(output, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_text + "\n")
        if args.verbose:
            print(f"\n  Results written to: {args.output}", file=sys.stderr)
    else:
        print(output_text)

    if args.verbose:
        print(f"\n  Accuracy: {accuracy:.0%} ({correct}/{total})", file=sys.stderr)


if __name__ == "__main__":
    main()
