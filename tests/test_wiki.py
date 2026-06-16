from __future__ import annotations

from pathlib import Path

import yaml

from scripts.build_site import SITE_ROOT, verify_site


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PAGE_FILES = {
    "content/index.md",
    "content/pages/getting-started.md",
    "content/pages/tools-and-recipes.md",
    "content/pages/resources.md",
}


def _assert_pages_collection(config: dict) -> None:
    assert config["media_folder"] == "content/media"
    assert len(config["collections"]) == 1
    collection = config["collections"][0]
    assert collection["name"] == "pages"
    assert "folder" not in collection
    files = collection["files"]
    assert {entry["file"] for entry in files} == EXPECTED_PAGE_FILES
    for entry in files:
        field_names = [field["name"] for field in entry["fields"]]
        assert field_names == ["body"]


def test_decap_editor_uses_a_files_pages_collection() -> None:
    config = yaml.safe_load((ROOT / "admin" / "config.yml").read_text("utf-8"))

    assert config["backend"]["name"] == "github"
    assert config["backend"]["branch"] == "main"
    assert config["public_folder"] == "REPLACE_WITH_MEDIA_PATH"
    _assert_pages_collection(config)


def test_netlify_broker_config_matches() -> None:
    config = yaml.safe_load(
        (ROOT / "oauth-broker" / "admin" / "config.yml").read_text("utf-8")
    )

    assert config["backend"]["name"] == "github"
    assert config["backend"]["repo"] == "simo-berrada/wiki"
    assert config["backend"]["branch"] == "main"
    _assert_pages_collection(config)


def test_admin_index_self_hosts_the_editor() -> None:
    index = (ROOT / "admin" / "index.html").read_text("utf-8")

    assert 'rel="cms-config-url"' in index
    assert "decap-cms" in index
    # The editor is served from the wiki itself, not a redirect to Netlify.
    assert "http-equiv" not in index


def test_github_pages_workflow_builds_and_deploys() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "pages.yml"
    ).read_text(encoding="utf-8")

    assert "actions/configure-pages@v5" in workflow
    assert "actions/upload-pages-artifact@v3" in workflow
    assert "actions/deploy-pages@v4" in workflow
    assert "python scripts/build_site.py" in workflow


def test_built_site_contains_wiki_and_editor() -> None:
    if not SITE_ROOT.exists():
        raise AssertionError("Run scripts/build_site.py before the test suite")

    assert (SITE_ROOT / "index.html").exists()
    assert (SITE_ROOT / "search" / "search_index.json").exists()
    assert (SITE_ROOT / "admin" / "index.html").exists()
    assert (SITE_ROOT / "admin" / "config.yml").exists()
    admin_index = (SITE_ROOT / "admin" / "index.html").read_text(encoding="utf-8")
    assert "decap-cms" in admin_index
    verify_site()
