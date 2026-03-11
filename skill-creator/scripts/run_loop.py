#!/usr/bin/env python3
"""
Run the eval-improve loop for skill description optimization.

Iteratively evaluates a skill description against a set of trigger queries,
calls an AI model to improve the description based on failures, and repeats.
Uses a train/test split to avoid overfitting.

## AI CLI Configuration

This script invokes an AI model via CLI subprocess. Configure via environment variables:

  AI_CLI_COMMAND   - The CLI command to invoke the AI model.
                     Default: auto-detects from available CLIs (claude, aider, etc.)
                     Examples:
                       "claude -p"           (Claude Code CLI)
                       "aider --message"     (Aider CLI)
                       "sgpt"               (Shell GPT)
                       "llm"                (Simon Willison's llm tool)

  AI_CLI_FLAGS     - Additional flags to pass to the CLI (optional).

See run_eval.py and improve_description.py for full CLI configuration docs.

Usage:
    python -m scripts.run_loop \\
      --eval-set /path/to/eval_set.json \\
      --skill-path /path/to/my-skill \\
      --model <model-id> \\
      --max-iterations 5 \\
      --verbose

The script:
  1. Splits the eval set into 60% train / 40% test
  2. Evaluates the current description (3 runs per query)
  3. Calls AI to improve the description based on train failures
  4. Re-evaluates the new description on both train and test
  5. Repeats up to --max-iterations times
  6. Selects the best description by test score (to avoid overfitting)
  7. Generates an HTML report and returns the best description
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

# Import sibling modules
try:
    from scripts.run_eval import run_eval_set
    from scripts.improve_description import build_improvement_prompt, extract_description, _call_ai_cli
    from scripts.utils import parse_skill_md
except ImportError:
    # Allow running as standalone
    from run_eval import run_eval_set
    from improve_description import build_improvement_prompt, extract_description, _call_ai_cli
    from utils import parse_skill_md


def split_eval_set(
    eval_set: list[dict], train_ratio: float = 0.6, seed: int | None = None
) -> tuple[list[dict], list[dict]]:
    """Split eval set into train and test sets.

    Stratified split: maintains the ratio of should_trigger=True/False
    in both train and test sets.
    """
    if seed is not None:
        random.seed(seed)

    positive = [e for e in eval_set if e["should_trigger"]]
    negative = [e for e in eval_set if not e["should_trigger"]]

    random.shuffle(positive)
    random.shuffle(negative)

    pos_split = max(1, int(len(positive) * train_ratio))
    neg_split = max(1, int(len(negative) * train_ratio))

    train = positive[:pos_split] + negative[:neg_split]
    test = positive[pos_split:] + negative[neg_split:]

    random.shuffle(train)
    random.shuffle(test)

    return train, test


def run_iteration(
    iteration: int,
    description: str,
    train_set: list[dict],
    test_set: list[dict],
    skill_path: str,
    skill_name: str,
    model: str | None,
    runs: int,
    timeout: int,
    verbose: bool,
) -> dict:
    """Run one iteration: evaluate on train and test sets.

    Returns dict with train_results, test_results, train_accuracy, test_accuracy.
    """
    if verbose:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"  Iteration {iteration}", file=sys.stderr)
        print(f"  Description: {description[:100]}...", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

    # Evaluate on train set
    if verbose:
        print(f"\n  [Train set: {len(train_set)} queries]", file=sys.stderr)
    train_results = run_eval_set(
        eval_set=train_set,
        skill_path=skill_path,
        skill_name=skill_name,
        description=description,
        model=model,
        runs=runs,
        timeout=timeout,
        verbose=verbose,
    )
    train_correct = sum(1 for r in train_results if r["correct"])
    train_accuracy = train_correct / len(train_results) if train_results else 0.0

    # Evaluate on test set
    if verbose:
        print(f"\n  [Test set: {len(test_set)} queries]", file=sys.stderr)
    test_results = run_eval_set(
        eval_set=test_set,
        skill_path=skill_path,
        skill_name=skill_name,
        description=description,
        model=model,
        runs=runs,
        timeout=timeout,
        verbose=verbose,
    )
    test_correct = sum(1 for r in test_results if r["correct"])
    test_accuracy = test_correct / len(test_results) if test_results else 0.0

    if verbose:
        print(f"\n  Train accuracy: {train_accuracy:.0%} ({train_correct}/{len(train_results)})", file=sys.stderr)
        print(f"  Test accuracy:  {test_accuracy:.0%} ({test_correct}/{len(test_results)})", file=sys.stderr)

    return {
        "iteration": iteration,
        "description": description,
        "train_results": train_results,
        "test_results": test_results,
        "train_accuracy": train_accuracy,
        "test_accuracy": test_accuracy,
    }


def improve_description(
    description: str,
    train_results: list[dict],
    skill_name: str,
    skill_path: str,
    skill_body: str = "",
) -> str | None:
    """Call AI to improve the description based on train set results."""
    prompt = build_improvement_prompt(
        skill_name=skill_name,
        current_description=description,
        eval_results=train_results,
        skill_body=skill_body,
    )

    response = _call_ai_cli(prompt)
    if not response:
        return None

    return extract_description(response)


def generate_report_html(iterations: list[dict], skill_name: str) -> str:
    """Generate a simple HTML report from iteration results."""
    rows = ""
    for it in iterations:
        is_best = it.get("is_best", False)
        row_class = 'style="background: #e8f5e9; font-weight: bold;"' if is_best else ""
        best_badge = " ★" if is_best else ""
        rows += f"""
        <tr {row_class}>
            <td>{it['iteration']}{best_badge}</td>
            <td>{it['train_accuracy']:.0%}</td>
            <td>{it['test_accuracy']:.0%}</td>
            <td><details><summary>Show</summary><pre style="white-space: pre-wrap; max-width: 600px;">{it['description']}</pre></details></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Description Optimization: {skill_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #f5f5f5; }}
        tr:hover {{ background: #f9f9f9; }}
        .summary {{ background: #f0f7ff; padding: 15px; border-radius: 8px; margin: 15px 0; }}
    </style>
</head>
<body>
    <h1>Description Optimization: {skill_name}</h1>
    <div class="summary">
        <strong>Iterations:</strong> {len(iterations)} |
        <strong>Best iteration:</strong> {next((i['iteration'] for i in iterations if i.get('is_best')), '?')} |
        <strong>Best test accuracy:</strong> {max((i['test_accuracy'] for i in iterations), default=0):.0%}
    </div>
    <table>
        <thead>
            <tr>
                <th>Iteration</th>
                <th>Train Accuracy</th>
                <th>Test Accuracy</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Run the eval-improve loop")
    parser.add_argument("--eval-set", required=True, type=Path, help="Path to eval set JSON")
    parser.add_argument("--skill-path", required=True, type=Path, help="Path to skill directory")
    parser.add_argument("--model", type=str, default=None, help="Model identifier")
    parser.add_argument(
        "--max-iterations", type=int, default=5, help="Max improvement iterations (default: 5)"
    )
    parser.add_argument("--runs", type=int, default=3, help="Runs per query (default: 3)")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per query in seconds")
    parser.add_argument(
        "--train-ratio", type=float, default=0.6, help="Train set ratio (default: 0.6)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for split")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output JSON file")
    parser.add_argument(
        "--report", type=Path, default=None, help="Output HTML report path"
    )
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
        skill_name, current_description, skill_content = parse_skill_md(args.skill_path)
    except Exception as e:
        print(f"Error parsing SKILL.md: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"  Skill: {skill_name}", file=sys.stderr)
        print(f"  Initial description: {current_description[:100]}...", file=sys.stderr)
        print(f"  Eval set size: {len(eval_set)}", file=sys.stderr)
        print(f"  Max iterations: {args.max_iterations}", file=sys.stderr)

    # Split into train/test
    train_set, test_set = split_eval_set(eval_set, args.train_ratio, args.seed)
    if args.verbose:
        train_pos = sum(1 for e in train_set if e["should_trigger"])
        test_pos = sum(1 for e in test_set if e["should_trigger"])
        print(f"  Train: {len(train_set)} ({train_pos} positive, {len(train_set) - train_pos} negative)", file=sys.stderr)
        print(f"  Test:  {len(test_set)} ({test_pos} positive, {len(test_set) - test_pos} negative)", file=sys.stderr)

    # Run iterations
    iterations: list[dict] = []
    description = current_description

    for i in range(args.max_iterations + 1):  # +1 for initial evaluation
        result = run_iteration(
            iteration=i,
            description=description,
            train_set=train_set,
            test_set=test_set,
            skill_path=skill_path,
            skill_name=skill_name,
            model=args.model,
            runs=args.runs,
            timeout=args.timeout,
            verbose=args.verbose,
        )
        iterations.append(result)

        # If this is the last iteration, or both train and test are 100%, stop
        if i == args.max_iterations:
            break
        if result["train_accuracy"] == 1.0 and result["test_accuracy"] == 1.0:
            if args.verbose:
                print("\n  Perfect scores on both sets! Stopping early.", file=sys.stderr)
            break

        # Improve description for next iteration
        if args.verbose:
            print(f"\n  Improving description...", file=sys.stderr)

        new_desc = improve_description(
            description=description,
            train_results=result["train_results"],
            skill_name=skill_name,
            skill_path=skill_path,
            skill_body=skill_content,
        )

        if not new_desc:
            if args.verbose:
                print("  WARNING: AI failed to produce a new description. Stopping.", file=sys.stderr)
            break

        if new_desc == description:
            if args.verbose:
                print("  Description unchanged, stopping.", file=sys.stderr)
            break

        description = new_desc

    # Select best by test score (breaks ties by train score, then earlier iteration)
    best_idx = max(
        range(len(iterations)),
        key=lambda i: (iterations[i]["test_accuracy"], iterations[i]["train_accuracy"], -i),
    )
    iterations[best_idx]["is_best"] = True
    best = iterations[best_idx]

    if args.verbose:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"  Best: iteration {best['iteration']}", file=sys.stderr)
        print(f"  Test accuracy: {best['test_accuracy']:.0%}", file=sys.stderr)
        print(f"  Train accuracy: {best['train_accuracy']:.0%}", file=sys.stderr)
        print(f"  Description: {best['description'][:200]}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

    # Build output
    output = {
        "skill_name": skill_name,
        "model": args.model,
        "best_description": best["description"],
        "best_iteration": best["iteration"],
        "best_test_accuracy": best["test_accuracy"],
        "best_train_accuracy": best["train_accuracy"],
        "initial_description": current_description,
        "total_iterations": len(iterations),
        "iterations": [
            {
                "iteration": it["iteration"],
                "description": it["description"],
                "train_accuracy": it["train_accuracy"],
                "test_accuracy": it["test_accuracy"],
                "is_best": it.get("is_best", False),
            }
            for it in iterations
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Write output
    output_text = json.dumps(output, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_text + "\n")
        if args.verbose:
            print(f"\n  Results written to: {args.output}", file=sys.stderr)
    else:
        print(output_text)

    # Generate report
    report_path = args.report
    if not report_path and args.output:
        report_path = args.output.with_suffix(".html")

    if report_path:
        html = generate_report_html(iterations, skill_name)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(html)
        if args.verbose:
            print(f"  Report written to: {report_path}", file=sys.stderr)
        try:
            webbrowser.open(f"file://{report_path.resolve()}")
        except Exception:
            pass  # Headless environments won't have a browser


if __name__ == "__main__":
    main()
