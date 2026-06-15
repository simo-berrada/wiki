# WOAH Data Science Wiki

A single public Data Science wiki with a browser-based editor.

- Wiki: `/`
- Editor for approved GitHub collaborators: `/admin/`
- Hosting: GitHub Pages
- Automated builds: GitHub Actions
- Content: `content/articles/`

Everything published by this project is public. Do not add confidential,
personal, regulated, or security-sensitive information.

## Local setup

Python 3.12 is supported.

```powershell
uv venv --python 3.12
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.\.venv\Scripts\python.exe scripts\build_site.py
.\.venv\Scripts\python.exe -m pytest -q
```

If OneDrive locks generated folders:

```powershell
$env:WIKI_BUILD_ROOT = "C:\tmp\woah-wiki-build"
$env:WIKI_SITE_ROOT = "C:\tmp\woah-wiki-site"
.\.venv\Scripts\python.exe scripts\build_site.py
```

Preview:

```powershell
.\.venv\Scripts\python.exe -m http.server 8000 --directory site
```

## Publishing

GitHub Actions validates, tests, builds, and deploys every push to `main`.
Complete the initial setup in [OPERATIONS.md](OPERATIONS.md).

The workflow automatically fills the GitHub repository and Pages URL into the
built Decap configuration. The repository variable `DECAP_SITE_DOMAIN`
identifies the separately hosted Netlify OAuth broker required for GitHub login.
