from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    references: tuple[str, ...]


def _parse_frontmatter(content: str) -> dict[str, str]:
    if not content.startswith("---\n"):
        raise ValueError("SKILL.md missing YAML frontmatter header")

    lines = content.splitlines()
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        raise ValueError("SKILL.md has unterminated YAML frontmatter")

    frontmatter: dict[str, str] = {}
    for line in lines[1:end_idx]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()
    return frontmatter


def load_skills(source_dir: Path) -> list[Skill]:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source skills directory not found: {source_dir}")

    skills: list[Skill] = []
    for skill_dir in sorted(p for p in source_dir.iterdir() if p.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8")
        frontmatter = _parse_frontmatter(content)
        name = frontmatter.get("name", "").strip()
        description = frontmatter.get("description", "").strip()
        if not name or not description:
            raise ValueError(f"Invalid skill frontmatter in: {skill_file}")

        references_dir = skill_dir / "references"
        references: list[str] = []
        if references_dir.exists():
            for ref in sorted(references_dir.glob("*.md")):
                references.append(f"references/{ref.name}")

        skills.append(Skill(name=name, description=description, references=tuple(references)))

    if not skills:
        raise ValueError(f"No skills found in source directory: {source_dir}")

    return skills
