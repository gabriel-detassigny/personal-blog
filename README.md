# blog.detassigny.net

Static blog built with [Zensical](https://zensical.org). Every push to `main` builds the site and deploys it with rsync to the web server.

## Writing a post

Create `docs/posts/YYYY-MM-DD-my-post.md`:

```markdown
---
date: 2026-10-12
authors:
  - gabriel
slug: my-post
description: One-line summary used by search engines and the RSS feed
---

# My post title

A short intro, shown on the home page.

<!-- more -->

The rest of the post.
```

- The post is served at `/<slug>/`.
- Put images in `docs/posts/images/` and reference them as `![alt](images/file.png)`.
- Link to other posts by their source file, e.g. `[Value Object](2018-11-29-design-pattern-1-value-object.md)`.
- Add `draft: true` to the front matter to keep a post out of the published site.

## Local preview

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/zensical serve        # http://localhost:8000
.venv/bin/zensical build --clean --strict
```

## Deployment

`.github/workflows/deploy.yml` builds the site, copies `deploy/.htaccess` (redirects from the old simple-blog URLs) into it, and rsyncs `site/` to the server. It needs these repository secrets:

| Secret | Value |
| --- | --- |
| `SSH_HOST` | server hostname or IP |
| `SSH_USER` | SSH user allowed to write to `DEPLOY_PATH` |
| `SSH_PRIVATE_KEY` | private key of a dedicated deploy key pair |
| `SSH_KNOWN_HOSTS` | output of `ssh-keyscan <host>` |
| `DEPLOY_PATH` | web root, e.g. `/var/www/blog-static` |

Without those secrets the deploy job is skipped (the build still runs as a check).

### One-time server cut-over

1. `mkdir /var/www/blog-static` on the server, owned by the deploy user, and add the deploy public key to that user's `~/.ssh/authorized_keys`.
2. Set the secrets above and re-run the workflow (Actions → Deploy → Run workflow).
3. Point the Apache vhost for `blog.detassigny.net` at the new directory:

   ```apache
   DocumentRoot /var/www/blog-static
   <Directory /var/www/blog-static>
       AllowOverride FileInfo
       Require all granted
   </Directory>
   ```

   Enable `mod_rewrite` (`a2enmod rewrite`) and reload Apache.
4. Check that `curl -I https://blog.detassigny.net/posts/12/x` returns a 301 to the new post URL.
5. Keep the old PHP app directory and a MySQL dump as a backup until you're happy, then remove them.

## Migration

`scripts/migrate.py` is the one-off script that exported the 12 posts and their images from the old simple-blog site. It's kept for reference and doesn't need to be run again.
