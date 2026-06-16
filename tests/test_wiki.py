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


def test_netlify_editor_uses_same_origin_login() -> None:
    config = yaml.safe_load(
        (ROOT / "oauth-broker" / "admin" / "config.yml").read_text("utf-8")
    )
    backend = config["backend"]

    assert backend["name"] == "github"
    assert backend["repo"] == "simo-berrada/wiki"
    assert backend["branch"] == "main"
    # Login goes through our own function on the same Netlify site, not the
    # cross-site api.netlify.com broker.
    assert backend["auth_endpoint"] == ".netlify/functions/auth"
    assert backend["base_url"].startswith("https://")
    assert "api.netlify.com" not in backend["base_url"]
    assert "site_domain" not in backend
    _assert_pages_collection(config)


def test_oauth_functions_exist() -> None:
    functions = ROOT / "netlify" / "functions"
    assert (functions / "auth.js").exists()
    callback = (functions / "callback.js").read_text("utf-8")
    # The handshake strings Decap CMS listens for.
    assert "authorizing:github" in callback
    assert "authorization:github:" in callback


def test_admin_index_redirects_to_the_editor() -> None:
    index = (ROOT / "admin" / "index.html").read_text("utf-8")

    # On GitHub Pages /admin/ is a redirect to the Netlify-hosted editor.
    assert "http-equiv" in index
    assert "REPLACE_WITH_DECAP_SITE_DOMAIN/admin/" in index


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
    assert "/admin/" in admin_index
    verify_site()
