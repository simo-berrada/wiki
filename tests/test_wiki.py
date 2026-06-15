from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from scripts.build_site import SITE_ROOT, verify_site
from scripts.validate_content import CONTENT_ROOT, validate_content


ROOT = Path(__file__).resolve().parents[1]


def test_repository_content_is_valid() -> None:
    assert validate_content() == []


def test_missing_media_is_rejected(tmp_path: Path) -> None:
    copied_content = tmp_path / "content"
    shutil.copytree(CONTENT_ROOT, copied_content)
    article = copied_content / "articles" / "missing-media.md"
    article.write_text(
        """---
title: Missing media
summary: This article should fail validation.
topic: Foundations
audience: Beginner
tags: []
author: Test
updated: 2026-06-15
---

![Missing file](/media/missing.png)
""",
        encoding="utf-8",
    )

    errors = validate_content(copied_content)
    assert any("referenced media does not exist" in error for error in errors)


def test_decap_has_one_public_article_collection() -> None:
    config = yaml.safe_load((ROOT / "admin" / "config.yml").read_text("utf-8"))

    assert config["backend"]["name"] == "github"
    assert config["backend"]["branch"] == "main"
    assert config["media_folder"] == "content/media"
    assert config["public_folder"] == "REPLACE_WITH_MEDIA_PATH"
    assert len(config["collections"]) == 1
    collection = config["collections"][0]
    assert collection["folder"] == "content/articles"
    assert collection["media_folder"] == "content/media"


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
    assert not (SITE_ROOT / "internal").exists()
    verify_site()
