# arpit-jain.com

Arpit Jain's personal site and the orange-bot blog. Plain Jekyll, built by GitHub Pages: push to
`main` and it deploys. No theme; the look is `assets/css/site.css`.

- `index.html`: home (profile and bio, featured projects, latest writing and news, selected
  publications, experience, the scholarship); `writings/`, `projects/`, `publications/`, `community/`,
  `news/` are the section pages.
- **Content model.** `_data/themes.yml` lists the themes. A project (`_projects/<slug>.md`: `title`,
  `theme`, `status`, `summary`, `repo` or `code`, `featured`, `order`, optional `planned` series) and a
  post (`_posts/YYYY-MM-DD-slug.md`) each name a theme; a post may also name a `project` (its slug) and
  a `series_order`, and then takes the project's theme. Projects without writing and writing without a
  project are both fine. `featured: true` puts a project on the home page.
- `_data/publications.yml` (pdf, arxiv, doi, abstract, bibtex), `_data/news.yml`, `_data/community.yml`,
  `_data/experience.yml`.

Post front matter: `title`, `subtitle`, `project`, `series_order`, `theme` (if no project), `series`,
`rig` (e.g. `v3`), `tags`. In a post, a blockquote is a "Where this sits" aside, and
`<div class="do-this" markdown="1">` is the "Do this on your SO-101" box.

Local preview: Homebrew `ruby@3.3` and the `github-pages` gem in `vendor/bundle`:
`LANG=en_US.UTF-8 PATH=/opt/homebrew/opt/ruby@3.3/bin:$PATH bundle exec jekyll serve --drafts`
(`.claude/launch.json` runs this). `_drafts/` is gitignored: example stubs for the preview only.

**Domain:** the site moves to https://arpit-jain.com once the DNS records are in Cloudflare (A and AAAA
for `@` to GitHub Pages, a CNAME for `www`, all "DNS only"): then add a `CNAME` file containing
`arpit-jain.com`, set `url` in `_config.yml`, and turn on "Enforce HTTPS" in the repo's Pages settings.
