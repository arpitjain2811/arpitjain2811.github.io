#!/usr/bin/env python3
"""Copy the blog drafts from the private orange-bot repo into this site's local preview.

Drafts stay private: `_drafts/` and `assets/drafts/` are gitignored, so nothing here is ever pushed.
The source of truth is ~/workspace/orange-bot/docs/blog/; edit there, then run this again.

  python3 scripts/sync_drafts.py

What it does to each draft: points `figures/...` at /assets/drafts/..., turns `<!-- ARPIT: ... -->`
notes into visible callouts, highlights [BRACKETED] placeholders, and marks the page as a draft.
"""
import os, re, shutil
SRC = os.path.expanduser('~/workspace/orange-bot/docs/blog')
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS = {  # source file -> (draft slug, date shown)
    '00-the-rig.md': ('meet-orange-bot', '2026-10-12'),
    '01-follow-a-pointer.md': ('follow-a-pointer', '2026-10-13'),
}

def convert(text, date):
    head, body = text.split('\n---\n', 1)
    head += f'\ndate: {date}\ndraft: true'
    # each figure URL carries its file's mtime, so the browser never shows a stale copy
    def url(path):
        f = os.path.join(SRC, 'figures', path)
        return f'/assets/drafts/{path}?v={int(os.path.getmtime(f)) if os.path.exists(f) else 0}'
    body = re.sub(r'\b(src|poster)="figures/([^"?]+)"', lambda m: f'{m.group(1)}="{url(m.group(2))}"', body)
    body = re.sub(r'\]\(figures/([^)\s?]+)\)', lambda m: f']({url(m.group(1))})', body)
    # the planner's notes to Arpit: visible in the preview
    body = re.sub(r'<!--\s*ARPIT:\s*(.*?)\s*-->', lambda m: '<aside class="arpit-note" markdown="0"><b>For you:</b> '
                  + re.sub(r'\s+', ' ', m.group(1)) + '</aside>', body, flags=re.S)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)   # other comments stay out
    # [PHOTO: ...] / [FIGURE ...] lines that are still missing
    body = re.sub(r'^\*\*\[(PHOTO|FIGURE|CLIP|VIDEO)([^\]]*)\]\*\*$', r'<div class="placeholder">\1\2</div>', body, flags=re.M)
    # [CAPS ...] or [$...] placeholders to fill in (not markdown links)
    body = re.sub(r'\[((?:ARPIT|\$|[A-Z][A-Z0-9 ,]+\$)[^\]]*)\](?!\()', r'<mark class="todo">\1</mark>', body)
    return head + '\n---\n' + body

os.makedirs(f'{SITE}/_drafts', exist_ok=True)
for src, (slug, date) in DRAFTS.items():
    with open(f'{SRC}/{src}') as f:
        out = convert(f.read(), date)
    with open(f'{SITE}/_drafts/{slug}.md', 'w') as f:
        f.write(out)
    print('draft', slug)
dst = f'{SITE}/assets/drafts'
if os.path.isdir(f'{SRC}/figures'):
    tmp = dst + '.tmp'
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(f'{SRC}/figures', tmp)
    shutil.rmtree(dst, ignore_errors=True)
    os.replace(tmp, dst)          # swap in whole, so the preview never serves half-copied files
    print('figures ->', dst)
