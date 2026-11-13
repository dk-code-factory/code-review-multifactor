"""Validate the plugin's host skills, manifests, catalogs, and release version."""

import json
from pathlib import Path
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = "code-review-multifactor"
SKILL = "code-review-multifactor"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    data = json.loads((ROOT / path).read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path}: expected a JSON object")
    require(data.get("name") == PLUGIN, f"{path}: unexpected plugin name")
    return data


def validate_skill(host):
    path = f"{host}/skills/{SKILL}/SKILL.md"
    text = (ROOT / path).read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    require(match is not None, f"{path}: missing YAML frontmatter")
    metadata = yaml.safe_load(match.group(1))
    require(isinstance(metadata, dict), f"{path}: frontmatter must be a mapping")
    require(metadata.get("name") == SKILL, f"{path}: unexpected skill name")
    description = metadata.get("description")
    require(isinstance(description, str) and description.strip(),
            f"{path}: description must be a nonempty string")
    require(text[match.end():].strip(), f"{path}: missing skill instructions")
    if host == "codex":
        allowed = {"name", "description", "license", "allowed-tools", "metadata"}
        require(not set(metadata) - allowed, f"{path}: unsupported frontmatter fields")
        require(len(description) <= 1024 and "<" not in description and ">" not in description,
                f"{path}: invalid Codex description")
    else:
        hint = metadata.get("argument-hint")
        require(isinstance(hint, str) and hint.strip(),
                f"{path}: argument-hint must be a nonempty string")


def main():
    manifests = []
    for host, directory in (("codex", ".codex-plugin"), ("claude", ".claude-plugin")):
        validate_skill(host)
        manifest = read_json(f"{directory}/plugin.json")
        require(manifest.get("skills") == f"./{host}/skills/",
                f"{directory}/plugin.json: incorrect host skill directory")
        manifests.append(manifest)

    version = manifests[0].get("version")
    require(isinstance(version, str) and re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][\w.+-]+)?", version),
            "Codex plugin version must be a semantic version")
    require(manifests[1].get("version") == version, "Host plugin versions differ")

    for path in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
        catalog = read_json(path)
        entries = catalog.get("plugins")
        require(isinstance(entries, list) and len(entries) == 1 and isinstance(entries[0], dict),
                f"{path}: expected this plugin's single catalog entry")
        entry = entries[0]
        require(entry.get("name") == PLUGIN, f"{path}: unexpected catalog plugin")
        if path.startswith(".claude-plugin"):
            require(entry.get("version") == version, f"{path}: catalog version differs")
            require(entry.get("source") == "./", f"{path}: incorrect plugin source")
        else:
            require(entry.get("source") == {"source": "local", "path": "./"},
                    f"{path}: incorrect plugin source")

    require(f"Version {version}." in (ROOT / "README.md").read_text(encoding="utf-8"),
            "README version differs from plugin manifests")
    print(f"Validated both host skills and plugin metadata for version {version}.")


if __name__ == "__main__":
    main()
