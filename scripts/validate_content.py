from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT / "content"
ARTICLES_ROOT = CONTENT_ROOT / "articles"

TOPICS = {
    "Foundations",
    "Data and Governance",
    "Statistics and Visualization",
    "Machine Learning and AI",
    "Engineering and MLOps",
    "Tools and Recipes",
    "WOAH Practice",
}
AUDIENCES = {"Beginner", "Practitioner", "Technical"}
REQUIRED_FIELDS = ("title", "summary", "topic", "audience", "author", "updated")

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
HTML_SOURCE_RE = re.compile(
    r"""(?:src|href)\s*=\s*["']([^"']+)["']""", re.IGNORECASE
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Article:
    path: Path
    metadata: dict
    body: str


def parse_front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML front matter")

    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"{path}: front matter is not closed with ---")

    metadata = yaml.safe_load(parts[1]) or {}
    if not isinstance(metadata, dict):
        raise ValueError(f"{path}: front matter must be a YAML mapping")
    return metadata, parts[2].lstrip("\r\n")


def load_articles(content_root: Path = CONTENT_ROOT) -> list[Article]:
    articles: list[Article] = []
    article_dir = content_root / "articles"
    if not article_dir.exists():
        return articles
    for path in sorted(article_dir.rglob("*.md")):
        metadata, body = parse_front_matter(path)
        articles.append(Article(path, metadata, body))
    return articles


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _is_valid_date(value: object) -> bool:
    if isinstance(value, (dt.date, dt.datetime)):
        return True
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " " in target:
        target = target.split(" ", 1)[0]
    return unquote(urlsplit(target).path)


def _validate_local_media(
    article: Article, target: str, content_root: Path
) -> str | None:
    if not target or target.startswith(("#", "mailto:", "tel:")):
        return None
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None

    path = _link_target(target)
    if not path or not re.search(
        r"\.(png|jpe?g|gif|svg|webp|pdf|csv|xlsx?)$", path, re.I
    ):
        return None

    media_match = re.match(r"^/(?:[^/]+/)*media/(.+)$", path, re.IGNORECASE)
    if media_match:
        resolved = content_root / "media" / media_match.group(1)
    elif path.startswith("/"):
        return (
            "local media must use /media/, a GitHub Pages "
            f"/<repository>/media/ path, or a relative path: {target}"
        )
    else:
        resolved = (article.path.parent / path).resolve()

    if not resolved.exists():
        return f"referenced media does not exist: {target}"
    return None


def validate_articles(
    articles: list[Article], content_root: Path = CONTENT_ROOT
) -> list[str]:
    errors: list[str] = []
    slugs: dict[str, Path] = {}

    for article in articles:
        prefix = _display_path(article.path)
        metadata = article.metadata

        for field in REQUIRED_FIELDS:
            value = metadata.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"{prefix}: missing required field '{field}'")

        if metadata.get("topic") not in TOPICS:
            errors.append(f"{prefix}: invalid topic '{metadata.get('topic')}'")
        if metadata.get("audience") not in AUDIENCES:
            errors.append(f"{prefix}: invalid audience '{metadata.get('audience')}'")
        if not _is_valid_date(metadata.get("updated")):
            errors.append(f"{prefix}: 'updated' must be a valid YYYY-MM-DD date")

        tags = metadata.get("tags", [])
        if tags is None:
            tags = []
        if not isinstance(tags, list) or any(
            not isinstance(tag, str) or not tag.strip() for tag in tags
        ):
            errors.append(f"{prefix}: 'tags' must be a list of non-empty strings")

        if not article.body.strip():
            errors.append(f"{prefix}: article body is empty")

        slug = article.path.stem.lower()
        if slug in slugs:
            errors.append(
                f"{prefix}: duplicate slug '{slug}' also used by "
                f"{_display_path(slugs[slug])}"
            )
        else:
            slugs[slug] = article.path

        targets = MARKDOWN_LINK_RE.findall(article.body)
        targets.extend(HTML_SOURCE_RE.findall(article.body))
        for target in targets:
            error = _validate_local_media(article, target, content_root)
            if error:
                errors.append(f"{prefix}: {error}")

    article_dir = content_root / "articles"
    if not article_dir.exists():
        errors.append(f"{_display_path(article_dir)}: article directory is missing")

    return errors


def validate_content(content_root: Path = CONTENT_ROOT) -> list[str]:
    try:
        articles = load_articles(content_root)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        return [str(exc)]
    return validate_articles(articles, content_root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate wiki article content.")
    parser.add_argument(
        "--content-root",
        type=Path,
        default=CONTENT_ROOT,
        help="Content directory containing articles/ and media/.",
    )
    args = parser.parse_args()

    errors = validate_content(args.content_root.resolve())
    if errors:
        print("Content validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    articles = load_articles(args.content_root.resolve())
    print(f"Validated {len(articles)} article(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
