from __future__ import annotations

from pathlib import Path


def load_template(template_dir: Path, name: str) -> str:
    template_path = template_dir / name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def render_template(template: str, values: dict[str, str]) -> str:
    return template.format(**values).rstrip() + "\n"
