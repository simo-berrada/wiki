# GitHub Pages setup for beginners

The finished system has one public wiki and one editor:

```text
https://YOUR-GITHUB-NAME.github.io/wiki/
https://YOUR-GITHUB-NAME.github.io/wiki/admin/
```

Anyone can read the wiki without an account. Only approved GitHub collaborators
can publish through the editor.

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

At this point the wiki works for readers. The editor page exists, but GitHub
login will not work until sections 4-6 are complete.

## 4. Create a GitHub OAuth application

The OAuth app allows the editor to ask GitHub who is signing in. Its secret must
never be committed to this public repository.

1. In GitHub, open your profile menu and select **Settings**.
2. Select **Developer settings**.
3. Select **OAuth Apps**.
4. Select **New OAuth App**.
5. Use:

```text
Application name: WOAH Data Science Wiki Editor
Homepage URL: https://YOUR-GITHUB-NAME.github.io/wiki/
Authorization callback URL: https://api.netlify.com/auth/done
```

6. Select **Register application**.
7. Record the **Client ID**.
8. Generate and record one **Client secret**.

Treat the client secret like a password.

## 5. Create the free OAuth broker

Decap's official GitHub backend requires a server for authentication. Netlify
provides that OAuth exchange service, even though the actual wiki remains hosted
on GitHub Pages.

1. Create a free account at <https://app.netlify.com>.
2. Select **Add new project > Import an existing project**.
3. Connect GitHub and select the public `wiki` repository.
4. Use these deployment settings:

```text
Build command: leave empty
Publish directory: oauth-broker
```

5. Deploy the project.
6. Record its URL, for example:

```text
https://woah-wiki-auth.netlify.app
```

7. In Netlify, open:
   **Project configuration > Access & security > OAuth**.
8. Under Authentication Providers, select **Install Provider**.
9. Select **GitHub**.
10. Enter the GitHub OAuth Client ID and Client secret.
11. Save.

The Netlify project is only the login broker. Readers continue to use the
GitHub Pages address.

## 6. Connect Decap to the OAuth broker

In the GitHub repository:

1. Select **Settings > Secrets and variables > Actions**.
2. Open the **Variables** tab.
3. Select **New repository variable**.
4. Name it exactly:

```text
DECAP_SITE_DOMAIN
```

5. Set its value to the Netlify project domain without `https://` or a trailing
   slash:

```text
woah-wiki-auth.netlify.app
```

6. Save.
7. Open **Actions > Build and deploy wiki**.
8. Select **Run workflow** on branch `main`.
9. Wait for the deployment to finish.

Then open:

```text
https://YOUR-GITHUB-NAME.github.io/wiki/admin/
```

Select **Login with GitHub** and approve the OAuth request.

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

1. Open `/admin/`.
2. Log in with an invited GitHub account.
3. Select **New Article**.
4. Complete all required fields.
5. Select **Publish**.
6. Confirm a new commit appears in the repository.
7. Wait for the GitHub Action to finish.
8. Confirm the article appears on the public wiki.

## Normal operation

Every edit follows this path:

1. Decap creates a commit in GitHub.
2. GitHub Actions validates the content.
3. MkDocs builds the website.
4. GitHub Pages deploys it.
5. The public site updates after a few minutes.

Technical contributors can also edit Markdown directly in `content/articles/`.

## Important limits

- Everything is public, including uploaded images and repository history.
- GitHub Pages does not provide private sections.
- Never commit the OAuth client secret.
- Editors must be GitHub collaborators with write access.
- Remove repository access when somebody should no longer edit.
- If an article fails validation, the live site remains on its previous version.

## Checklist

- [ ] Create a public GitHub repository.
- [ ] Push branch `main`.
- [ ] Enable GitHub Pages with GitHub Actions.
- [ ] Confirm the public wiki works.
- [ ] Create the GitHub OAuth application.
- [ ] Create the free Netlify OAuth broker.
- [ ] Add the `DECAP_SITE_DOMAIN` repository variable.
- [ ] Invite editors as GitHub collaborators.
- [ ] Publish and verify a test article.

References:

- [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Decap GitHub backend](https://decapcms.org/docs/github-backend/)
- [Netlify OAuth provider setup](https://docs.netlify.com/manage/security/secure-access-to-sites/oauth-provider-tokens/)
