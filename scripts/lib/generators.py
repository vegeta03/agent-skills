from __future__ import annotations

from pathlib import Path

from .skill_loader import Skill
from .template_tools import load_template, render_template

GEN_MARKER = "<!-- GENERATED: agent-skills/scripts/sync.py -->"

FRONTEND_APPLY_TO = "**/*.html,**/*.css,**/*.scss,**/*.sass,**/*.js,**/*.jsx,**/*.ts,**/*.tsx,**/*.vue,**/*.svelte"

SKILL_LABELS = {
    "explanatory-output-style": "Explanatory Output Style",
    "learning-output-style": "Learning Output Style",
    "code-review": "Code Review",
    "feature-dev": "Feature Development",
    "frontend-design": "Frontend Design",
    "ralph-wiggum": "Ralph Wiggum",
}


def _title(name: str) -> str:
    return SKILL_LABELS.get(name, name.replace("-", " ").title())


def _references_section(references: tuple[str, ...]) -> str:
    if not references:
        return ""
    lines = ["Also read if needed:"]
    for ref in references:
        lines.append(f"- `agent-skills/.agents/skills/{{name}}/{ref}`")
    return "\n".join(lines) + "\n\n"


def _cursor_invocation_frontmatter(invocation: str) -> str:
    if invocation == "manual":
        return "disable-model-invocation: true"
    if invocation in ("auto", "both"):
        return "disable-model-invocation: false"
    raise ValueError(f"Unsupported invocation mode: {invocation}")


def _copilot_skill_invocation(invocation: str) -> tuple[str, str]:
    if invocation == "auto":
        return ("false", "false")
    if invocation == "manual":
        return ("true", "true")
    if invocation == "both":
        return ("true", "false")
    raise ValueError(f"Unsupported invocation mode: {invocation}")


def generate_cursor_files(
    template_dir: Path, workspace: Path, skills: list[Skill], invocation: str
) -> dict[Path, str]:
    template = load_template(template_dir, "cursor-skill.md.tpl")
    output: dict[Path, str] = {}
    for skill in sorted(skills, key=lambda s: s.name):
        references = _references_section(skill.references).format(name=skill.name)
        content = render_template(
            template,
            {
                "name": skill.name,
                "title": _title(skill.name),
                "description": skill.description,
                "marker": GEN_MARKER,
                "references_section": references,
                "invocation_frontmatter": _cursor_invocation_frontmatter(invocation),
            },
        )
        output[workspace / ".cursor" / "skills" / skill.name / "SKILL.md"] = content
    return output


def generate_copilot_files(
    template_dir: Path, workspace: Path, skills: list[Skill], invocation: str
) -> dict[Path, str]:
    output: dict[Path, str] = {}

    repo_template = load_template(template_dir, "copilot-instructions.md.tpl")
    skill_lines = [
        f"- `{_title(skill.name)}`: `agent-skills/.agents/skills/{skill.name}/SKILL.md`"
        for skill in sorted(skills, key=lambda s: s.name)
    ]
    repo_content = render_template(
        repo_template,
        {
            "marker": GEN_MARKER,
            "skills_list": "\n".join(skill_lines),
        },
    )
    output[workspace / ".github" / "copilot-instructions.md"] = repo_content

    instruction_template = load_template(template_dir, "copilot-instruction.md.tpl")
    for skill in sorted(skills, key=lambda s: s.name):
        references = _references_section(skill.references).format(name=skill.name)
        apply_to = FRONTEND_APPLY_TO if skill.name == "frontend-design" else "**"
        content = render_template(
            instruction_template,
            {
                "apply_to": apply_to,
                "description": skill.description,
                "marker": GEN_MARKER,
                "title": _title(skill.name),
                "name": skill.name,
                "references_section": references,
            },
        )
        output[workspace / ".github" / "instructions" / f"{skill.name}.instructions.md"] = content

    # Copilot Agent Skills layer (.github/skills)
    skill_template = load_template(template_dir, "copilot-skill.md.tpl")
    user_invokable, disable_model_invocation = _copilot_skill_invocation(invocation)
    for skill in sorted(skills, key=lambda s: s.name):
        references = _references_section(skill.references).format(name=skill.name)
        content = render_template(
            skill_template,
            {
                "name": skill.name,
                "description": skill.description,
                "title": _title(skill.name),
                "marker": GEN_MARKER,
                "references_section": references,
                "user_invokable": user_invokable,
                "disable_model_invocation": disable_model_invocation,
            },
        )
        output[workspace / ".github" / "skills" / skill.name / "SKILL.md"] = content

    # Copilot Prompt Files layer (.github/prompts) for explicit slash invocation.
    prompt_template = load_template(template_dir, "copilot-prompt.prompt.md.tpl")
    for skill in sorted(skills, key=lambda s: s.name):
        references = _references_section(skill.references).format(name=skill.name)
        content = render_template(
            prompt_template,
            {
                "name": skill.name,
                "description": skill.description,
                "title": _title(skill.name),
                "marker": GEN_MARKER,
                "references_section": references,
            },
        )
        output[workspace / ".github" / "prompts" / f"{skill.name}.prompt.md"] = content

    return output


def generate_augment_files(
    template_dir: Path, workspace: Path, skills: list[Skill], invocation: str
) -> dict[Path, str]:
    template = load_template(template_dir, "augment-rule.md.tpl")
    output: dict[Path, str] = {}

    if invocation == "auto":
        variants = [("", "agent_requested", "Auto")]
    elif invocation == "manual":
        variants = [("", "manual", "Manual")]
    elif invocation == "both":
        variants = [(".auto", "agent_requested", "Auto"), (".manual", "manual", "Manual")]
    else:
        raise ValueError(f"Unsupported invocation mode: {invocation}")

    for skill in sorted(skills, key=lambda s: s.name):
        for suffix, rule_type, mode_label in variants:
            references = _references_section(skill.references).format(name=skill.name)
            description = skill.description
            if invocation == "both":
                description = f"{skill.description} {mode_label} variant."
            content = render_template(
                template,
                {
                    "description": description,
                    "marker": GEN_MARKER,
                    "title": _title(skill.name),
                    "name": skill.name,
                    "references_section": references,
                    "rule_type": rule_type,
                    "mode_label": mode_label,
                },
            )
            output[workspace / ".augment" / "rules" / f"{skill.name}{suffix}.md"] = content
    return output


def generate_agents_file(template_dir: Path, workspace: Path, skills: list[Skill]) -> dict[Path, str]:
    template = load_template(template_dir, "agents.md.tpl")
    routing_lines = [f"- `{_title(skill.name)}` -> `agent-skills/.agents/skills/{skill.name}/SKILL.md`" for skill in sorted(skills, key=lambda s: s.name)]
    content = render_template(
        template,
        {
            "marker": GEN_MARKER,
            "skills_routing": "\n".join(routing_lines),
        },
    )
    return {workspace / "AGENTS.md": content}
