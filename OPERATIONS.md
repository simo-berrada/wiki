# GitHub Pages setup for beginners

The finished system is one public wiki. You only ever share a single link:

```text
https://YOUR-GITHUB-NAME.github.io/wiki/
```

The editor is built into that site (an **Edit** button in the header, also
reachable at `/wiki/admin/`). A small Netlify service is used only behind the
scenes for the GitHub login — nobody needs to visit or share its address.

Anyone can read the wiki without an account. Only approved GitHub collaborators
can save changes through the editor.

## What you need

- A free GitHub account.
- A public GitHub repository.
- GitHub accounts for each editor.
- A small OAuth broker because GitHub does not allow a static browser page to
  safely hold an OAuth client secret.

The website and GitHub Actions are free for a public repository. The repository
files and generated website are both public.

## 1. Create the GitHub repository

1. Sign in at <https://github.com>.
2. Select **New repository**.
3. Choose your account or an approved WOAH GitHub organization as Owner.
4. Name the repository `wiki`.
5. Select **Public**.
6. Do not add a README, `.gitignore`, or license because they already exist.
7. Select **Create repository**.
8. Copy the HTTPS repository URL, for example:

```text
https://github.com/YOUR-GITHUB-NAME/wiki.git
```

## 2. Push this project to GitHub

This local repository currently points to Azure DevOps. Keep that remote as a
backup and add GitHub as a second remote:

```powershell
git remote rename origin azure
git remote add origin https://github.com/YOUR-GITHUB-NAME/wiki.git
git add .
git commit -m "Create public Data Science wiki"
git push -u origin main
```

Replace `YOUR-GITHUB-NAME` with the actual owner.

Success check: the files appear at
`https://github.com/YOUR-GITHUB-NAME/wiki`.

## 3. Enable GitHub Pages

1. Open the GitHub repository.
2. Select **Settings**.
3. Select **Pages** under **Code and automation**.
4. Under **Build and deployment**, set Source to **GitHub Actions**.
5. Open the repository's **Actions** tab.
6. Open the **Build and deploy wiki** workflow.
7. Wait for both `build` and `deploy` to become green.
8. Return to **Settings > Pages** and select **Visit site**.

The first deployment can take several minutes.

At this point the wiki works for readers. The built-in editor at `/admin/` needs
the GitHub login configured in sections 4-6 before anyone can save.

The editor and its login both run on a small **Netlify** site, so the GitHub
sign-in happens on a single web address and is not blocked by locked-down
corporate browsers. Sections 4-6 set this up once.

## 4. Create a GitHub OAuth application

The OAuth app lets the editor ask GitHub who is signing in. Its secret must never
be committed to this public repository.

1. In GitHub, open your profile menu and select **Settings**.
2. Select **Developer settings**.
3. Select **OAuth Apps**.
4. Select **New OAuth App**.
5. Use (replace the Netlify address with your own once you have it from step 5):

```text
Application name: WOAH Data Science Wiki Editor
Homepage URL: https://YOUR-NETLIFY-SITE.netlify.app/admin/
Authorization callback URL: https://YOUR-NETLIFY-SITE.netlify.app/.netlify/functions/callback
```

6. Select **Register application**.
7. Record the **Client ID**.
8. Generate and record one **Client secret**.

Treat the client secret like a password. The callback URL must match the Netlify
site exactly — if you rename the site later, update it here too.

## 5. Deploy the Netlify editor and login service

The repository already contains the editor (`oauth-broker/admin/`) and the login
functions (`netlify/functions/`). Netlify hosts both.

1. Create a free account at <https://app.netlify.com>.
2. Select **Add new project > Import an existing project**.
3. Connect GitHub and select the public `wiki` repository.
4. Use these deployment settings:

```text
Build command: leave empty
Publish directory: oauth-broker
Functions directory: netlify/functions   (already set in netlify.toml)
```

5. Deploy the project, then record its URL, for example:

```text
https://woah-wiki-auth.netlify.app
```

6. Open **Project configuration > Environment variables** and add two variables
   (from the GitHub OAuth app in step 4):

```text
OAUTH_CLIENT_ID      = <your Client ID>
OAUTH_CLIENT_SECRET  = <your Client secret>
```

7. Trigger a redeploy (**Deploys > Trigger deploy**) so the variables take effect.
8. If you used a placeholder Netlify address in step 4, go back and update the
   GitHub OAuth app's Homepage and callback URLs to the real Netlify address.

> The editor's address is baked into `oauth-broker/admin/config.yml`
> (`base_url:`). If your Netlify domain is **not**
> `iridescent-quokka-3f9b9b.netlify.app`, change that one line to your domain and
> push.

## 6. Point the wiki's Edit button at the editor

In the GitHub repository:

1. Select **Settings > Secrets and variables > Actions**.
2. Open the **Variables** tab.
3. Select **New repository variable** (or edit the existing one).
4. Name it exactly:

```text
DECAP_SITE_DOMAIN
```

5. Set its value to the Netlify domain without `https://` or a trailing slash:

```text
woah-wiki-auth.netlify.app
```

6. Save.
7. Open **Actions > Build and deploy wiki**.
8. Select **Run workflow** on branch `main`.
9. Wait for the deployment to finish.

Now the **Edit** button on the public wiki sends people to the Netlify editor.
Open it and select **Login with GitHub** to confirm sign-in completes.

## 7. Approve editors

Decap's GitHub backend only allows users with push access to publish.

For each editor:

1. Ask them to create a free GitHub account using any email address.
2. Open the repository.
3. Select **Settings > Collaborators**.
4. Select **Add people**.
5. Invite their GitHub username.
6. Ask them to accept the invitation.

For an organization-owned repository, use a team with repository write access
instead of adding people individually.

The repository is public, but only collaborators with write access can publish.

## 8. Test the workflow

### Reader

1. Open the Pages URL in a private browser window.
2. Confirm the wiki and search work without login.

### Editor

1. Open the wiki and click **Edit** in the header (or go to `/wiki/admin/`).
2. Log in with an invited GitHub account.
3. Open a page under **Pages**.
4. Change its content.
5. Select **Publish**.
6. Confirm a new commit appears in the repository.
7. Wait for the GitHub Action to finish.
8. Confirm the change appears on the public wiki.

## Normal operation

Every edit follows this path:

1. Decap creates a commit in GitHub.
2. GitHub Actions builds the website with MkDocs.
3. GitHub Pages deploys it.
4. The public site updates after a few minutes.

Technical contributors can also edit the Markdown pages directly in `content/`.
To add a new page, see [README.md](README.md).

## Important limits

- Everything is public, including uploaded images and repository history.
- GitHub Pages does not provide private sections.
- Never commit the OAuth client secret; it lives only in Netlify environment
  variables (`OAUTH_CLIENT_SECRET`).
- Editors must be GitHub collaborators with write access.
- Remove repository access when somebody should no longer edit.
- If a build fails, the live site remains on its previous version.

## Checklist

- [ ] Create a public GitHub repository.
- [ ] Push branch `main`.
- [ ] Enable GitHub Pages with GitHub Actions.
- [ ] Confirm the public wiki works.
- [ ] Create the GitHub OAuth application (callback = Netlify `/.netlify/functions/callback`).
- [ ] Deploy the Netlify editor (publish `oauth-broker`, functions `netlify/functions`).
- [ ] Set `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET` in Netlify and redeploy.
- [ ] Add the `DECAP_SITE_DOMAIN` repository variable.
- [ ] Invite editors as GitHub collaborators.
- [ ] Publish and verify a test edit.

References:

- [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Decap GitHub backend](https://decapcms.org/docs/github-backend/)
- [Decap external OAuth clients](https://decapcms.org/docs/external-oauth-clients/)
