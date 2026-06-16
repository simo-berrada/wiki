# WOAH Data Science Wiki

A small public Data Science wiki that anyone on the team can read, and approved
GitHub collaborators can edit.

- Wiki: `/`
- Editor (built into the site): click **Edit** in the header, or go to `/admin/`
- Hosting: GitHub Pages
- Automated builds: GitHub Actions
- Pages: `content/index.md` (home) and `content/pages/*.md`

Everything published by this project is public. Do not add confidential,
personal, regulated, or security-sensitive information.

## Editing

**In the browser (no setup needed):** open the wiki, click **Edit** in the top
bar, sign in with GitHub, pick a page, change its content, and publish. Only
GitHub collaborators with write access can save — see [OPERATIONS.md](OPERATIONS.md).

**In the repository (for technical contributors):** edit the Markdown files in
`content/`. Each page is plain Markdown — no required front matter.

To **add a new page**: create `content/pages/<name>.md`, add a line under `nav:`
in `mkdocs.yml`, and add a matching entry to the `files:` list in both
`admin/config.yml` and `oauth-broker/admin/config.yml`.

## Local setup

Python 3.12 is supported.

```powershell
uv venv --python 3.12
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.\.venv\Scripts\python.exe scripts\build_site.py
.\.venv\Scripts\python.exe -m pytest -q
```

If OneDrive locks the generated `site` folder:

```powershell
$env:WIKI_SITE_ROOT = "C:\tmp\woah-wiki-site"
.\.venv\Scripts\python.exe scripts\build_site.py
```

Preview:

```powershell
.\.venv\Scripts\python.exe -m http.server 8000 --directory site
```

(The **Edit** button appears in preview but GitHub login only works on the
deployed site, which has the OAuth broker configured.)

## Publishing

GitHub Actions builds, tests, and deploys every push to `main`. Complete the
initial setup in [OPERATIONS.md](OPERATIONS.md).

The workflow automatically fills the GitHub repository and Pages URL into the
built Decap configuration. The repository variable `DECAP_SITE_DOMAIN` identifies
the Netlify OAuth broker used invisibly for GitHub login.
