from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

import yaml

try:
    from .validate_content import CONTENT_ROOT, ROOT, load_articles, validate_content
except ImportError:
    from validate_content import CONTENT_ROOT, ROOT, load_articles, validate_content


BUILD_ROOT = Path(os.environ.get("WIKI_BUILD_ROOT", ROOT / ".build")).resolve()
SITE_ROOT = Path(os.environ.get("WIKI_SITE_ROOT", ROOT / "site")).resolve()


def _render_front_matter(metadata: dict, body: str) -> str:
    front_matter = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).rstrip()
    return f"---\n{front_matter}\n---\n\n{body.lstrip()}"


def prepare_content() -> None:
    if BUILD_ROOT.exists():
        shutil.rmtree(BUILD_ROOT)
    shutil.copytree(CONTENT_ROOT, BUILD_ROOT / "content")

    for article in load_articles():
        metadata = dict(article.metadata)
        original_tags = metadata.get("tags") or []
        metadata["tags"] = list(
            dict.fromkeys([metadata["topic"], metadata["audience"], *original_tags])
        )
        destination = BUILD_ROOT / "content" / article.path.relative_to(CONTENT_ROOT)
        destination.write_text(
            _render_front_matter(metadata, article.body),
            encoding="utf-8",
        )


def run_mkdocs() -> None:
    environment = os.environ.copy()
    environment["WIKI_DOCS_DIR"] = str(BUILD_ROOT / "content")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            "mkdocs.yml",
            "--site-dir",
            str(SITE_ROOT),
        ],
        cwd=ROOT,
        env=environment,
        check=True,
    )


def _site_media_path(site_url: str) -> str:
    path = urlsplit(site_url).path.rstrip("/")
    return f"{path}/media" if path else "/media"


def install_admin() -> None:
    destination = SITE_ROOT / "admin"
    shutil.copytree(ROOT / "admin", destination)

    build_id = os.environ.get("GITHUB_SHA", "local")
    index_path = destination / "index.html"
    index = index_path.read_text(encoding="utf-8")
    index = index.replace("REPLACE_WITH_BUILD_ID", build_id)
    index_path.write_text(index, encoding="utf-8")

    config_path = destination / "config.yml"
    config = config_path.read_text(encoding="utf-8")
    repository = os.environ.get(
        "WIKI_GITHUB_REPOSITORY", "REPLACE_WITH_GITHUB_REPOSITORY"
    )
    site_domain = (
        os.environ.get("WIKI_DECAP_SITE_DOMAIN")
        or "REPLACE_WITH_DECAP_SITE_DOMAIN"
    )
    site_url = os.environ.get("WIKI_SITE_URL", "http://localhost:8000/")
    if not site_url.endswith("/"):
        site_url += "/"

    replacements = {
        "REPLACE_WITH_GITHUB_REPOSITORY": repository,
        "REPLACE_WITH_DECAP_SITE_DOMAIN": site_domain,
        "REPLACE_WITH_SITE_URL": site_url,
        "REPLACE_WITH_MEDIA_PATH": _site_media_path(site_url),
    }
    for placeholder, value in replacements.items():
        config = config.replace(placeholder, value)
    config_path.write_text(config, encoding="utf-8")


def assemble_site() -> None:
    if SITE_ROOT.exists():
        shutil.rmtree(SITE_ROOT)
    run_mkdocs()
    install_admin()
    (SITE_ROOT / ".nojekyll").touch()


def verify_site() -> None:
    required = (
        SITE_ROOT / "index.html",
        SITE_ROOT / "search" / "search_index.json",
        SITE_ROOT / "admin" / "index.html",
        SITE_ROOT / "admin" / "config.yml",
        SITE_ROOT / ".nojekyll",
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError("Built site is missing:\n- " + "\n- ".join(missing))

    config = (SITE_ROOT / "admin" / "config.yml").read_text(encoding="utf-8")
    index = (SITE_ROOT / "admin" / "index.html").read_text(encoding="utf-8")
    required_placeholders = (
        "REPLACE_WITH_GITHUB_REPOSITORY",
        "REPLACE_WITH_SITE_URL",
        "REPLACE_WITH_MEDIA_PATH",
    )
    if os.environ.get("GITHUB_ACTIONS") == "true" and any(
        placeholder in config for placeholder in required_placeholders
    ):
        raise RuntimeError(
            "GitHub Pages build contains unresolved editor configuration."
        )
    if "REPLACE_WITH_BUILD_ID" in index:
        raise RuntimeError("GitHub Pages build contains an unresolved build ID.")


def main() -> int:
    errors = validate_content()
    if errors:
        print("Content validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    prepare_content()
    assemble_site()
    verify_site()
    print(f"Built and verified site at {SITE_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
