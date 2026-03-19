"""Tests for the gen_copilot_instructions script."""

from pathlib import Path
from unittest.mock import patch

import pytest

from script import gen_copilot_instructions


def test_generate_output_contains_agents_content(tmp_path: Path) -> None:
    """Test that the generated output contains content from AGENTS.md."""
    agents_file = tmp_path / "AGENTS.md"
    agents_file.write_text("# Test Instructions\n\nSome instructions here.\n")

    skills_dir = tmp_path / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    output_file = tmp_path / ".github" / "copilot-instructions.md"
    output_file.parent.mkdir(parents=True)

    with (
        patch.object(gen_copilot_instructions, "AGENTS_FILE", agents_file),
        patch.object(gen_copilot_instructions, "SKILLS_DIR", skills_dir),
        patch.object(gen_copilot_instructions, "OUTPUT_FILE", output_file),
    ):
        content = gen_copilot_instructions.generate_output()

    assert "# Test Instructions" in content
    assert "Some instructions here." in content
    assert gen_copilot_instructions.GENERATED_MESSAGE in content


def test_generate_output_includes_skills(tmp_path: Path) -> None:
    """Test that the generated output includes skill references."""
    agents_file = tmp_path / "AGENTS.md"
    agents_file.write_text("# Instructions\n")

    skills_dir = tmp_path / ".claude" / "skills"
    skill_dir = skills_dir / "my-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("# My Skill\n\nSkill content.\n")

    output_file = tmp_path / ".github" / "copilot-instructions.md"
    output_file.parent.mkdir(parents=True)

    with (
        patch.object(gen_copilot_instructions, "AGENTS_FILE", agents_file),
        patch.object(gen_copilot_instructions, "SKILLS_DIR", skills_dir),
        patch.object(gen_copilot_instructions, "OUTPUT_FILE", output_file),
    ):
        content = gen_copilot_instructions.generate_output()

    assert "# Skills" in content
    assert "my-skill" in content
    assert str(skill_file) in content


def test_generate_output_excludes_specified_skills(tmp_path: Path) -> None:
    """Test that excluded skills are not included in output."""
    agents_file = tmp_path / "AGENTS.md"
    agents_file.write_text("# Instructions\n")

    skills_dir = tmp_path / ".claude" / "skills"
    excluded_skill_dir = skills_dir / "github-pr-reviewer"
    excluded_skill_dir.mkdir(parents=True)
    (excluded_skill_dir / "SKILL.md").write_text("# Excluded Skill\n")

    output_file = tmp_path / ".github" / "copilot-instructions.md"
    output_file.parent.mkdir(parents=True)

    with (
        patch.object(gen_copilot_instructions, "AGENTS_FILE", agents_file),
        patch.object(gen_copilot_instructions, "SKILLS_DIR", skills_dir),
        patch.object(gen_copilot_instructions, "OUTPUT_FILE", output_file),
    ):
        content = gen_copilot_instructions.generate_output()

    assert "github-pr-reviewer" not in content
    assert "# Skills" not in content


def test_generate_output_parses_skill_name_from_frontmatter(tmp_path: Path) -> None:
    """Test that skill names are parsed from YAML frontmatter."""
    agents_file = tmp_path / "AGENTS.md"
    agents_file.write_text("# Instructions\n")

    skills_dir = tmp_path / ".claude" / "skills"
    skill_dir = skills_dir / "my-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: My Custom Skill Name\n---\n# Content\n")

    output_file = tmp_path / ".github" / "copilot-instructions.md"
    output_file.parent.mkdir(parents=True)

    with (
        patch.object(gen_copilot_instructions, "AGENTS_FILE", agents_file),
        patch.object(gen_copilot_instructions, "SKILLS_DIR", skills_dir),
        patch.object(gen_copilot_instructions, "OUTPUT_FILE", output_file),
    ):
        content = gen_copilot_instructions.generate_output()

    assert "My Custom Skill Name" in content


def test_validate_passes_when_up_to_date(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that validation passes when the output file is up to date."""
    ha_root = tmp_path / "ha_root"
    ha_root.mkdir()
    (ha_root / "homeassistant").mkdir()

    agents_file = ha_root / "AGENTS.md"
    agents_file.write_text("# Instructions\n")

    skills_dir = ha_root / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    output_file = ha_root / ".github" / "copilot-instructions.md"
    output_file.parent.mkdir(parents=True)

    monkeypatch.chdir(ha_root)

    with (
        patch.object(gen_copilot_instructions, "AGENTS_FILE", agents_file),
        patch.object(gen_copilot_instructions, "SKILLS_DIR", skills_dir),
        patch.object(gen_copilot_instructions, "OUTPUT_FILE", output_file),
    ):
        # First generate the file
        gen_copilot_instructions.main(validate=False)
        # Then validate it
        result = gen_copilot_instructions.main(validate=True)

    assert result == 0


def test_validate_fails_when_out_of_date(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that validation fails when the output file is out of date."""
    ha_root = tmp_path / "ha_root"
    ha_root.mkdir()
    (ha_root / "homeassistant").mkdir()

    agents_file = ha_root / "AGENTS.md"
    agents_file.write_text("# Instructions\n")

    skills_dir = ha_root / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    output_file = ha_root / ".github" / "copilot-instructions.md"
    output_file.parent.mkdir(parents=True)
    output_file.write_text("# Outdated content\n")

    monkeypatch.chdir(ha_root)

    with (
        patch.object(gen_copilot_instructions, "AGENTS_FILE", agents_file),
        patch.object(gen_copilot_instructions, "SKILLS_DIR", skills_dir),
        patch.object(gen_copilot_instructions, "OUTPUT_FILE", output_file),
    ):
        result = gen_copilot_instructions.main(validate=True)

    assert result == 1


def test_validate_fails_when_output_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that validation fails when the output file does not exist."""
    ha_root = tmp_path / "ha_root"
    ha_root.mkdir()
    (ha_root / "homeassistant").mkdir()

    agents_file = ha_root / "AGENTS.md"
    agents_file.write_text("# Instructions\n")

    skills_dir = ha_root / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    output_file = ha_root / ".github" / "copilot-instructions.md"
    output_file.parent.mkdir(parents=True)

    monkeypatch.chdir(ha_root)

    with (
        patch.object(gen_copilot_instructions, "AGENTS_FILE", agents_file),
        patch.object(gen_copilot_instructions, "SKILLS_DIR", skills_dir),
        patch.object(gen_copilot_instructions, "OUTPUT_FILE", output_file),
    ):
        result = gen_copilot_instructions.main(validate=True)

    assert result == 1


def test_main_fails_when_not_in_ha_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that main fails when not run from the HA root directory."""
    monkeypatch.chdir(tmp_path)
    result = gen_copilot_instructions.main()

    assert result == 1


def test_gather_skills_returns_empty_when_no_skills_dir(tmp_path: Path) -> None:
    """Test that gather_skills returns empty list when skills dir doesn't exist."""
    nonexistent_dir = tmp_path / "nonexistent"

    with patch.object(gen_copilot_instructions, "SKILLS_DIR", nonexistent_dir):
        skills = gen_copilot_instructions.gather_skills()

    assert skills == []


def test_gather_skills_ignores_non_directories(tmp_path: Path) -> None:
    """Test that gather_skills ignores files (non-directories) in the skills dir."""
    skills_dir = tmp_path / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    # Create a file (not a directory) in the skills dir
    (skills_dir / "not-a-dir.md").write_text("# Not a skill dir\n")

    # Create a valid skill directory
    skill_dir = skills_dir / "real-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Real skill\n")

    with patch.object(gen_copilot_instructions, "SKILLS_DIR", skills_dir):
        skills = gen_copilot_instructions.gather_skills()

    assert len(skills) == 1
    assert skills[0][0] == "real-skill"


@pytest.mark.parametrize(
    ("frontmatter", "expected_name"),
    [
        ("---\nname: Custom Name\n---\n# Content\n", "Custom Name"),
        ("---\nother: value\n---\n# Content\n", "my-skill"),
        ("# No frontmatter\n", "my-skill"),
        ("---\nname: \n---\n# Content\n", "my-skill"),
    ],
)
def test_gather_skills_name_extraction(
    tmp_path: Path, frontmatter: str, expected_name: str
) -> None:
    """Test skill name extraction from frontmatter."""
    skills_dir = tmp_path / ".claude" / "skills"
    skill_dir = skills_dir / "my-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(frontmatter)

    with patch.object(gen_copilot_instructions, "SKILLS_DIR", skills_dir):
        skills = gen_copilot_instructions.gather_skills()

    assert len(skills) == 1
    assert skills[0][0] == expected_name
