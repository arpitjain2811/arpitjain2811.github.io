# Boiler Room runbook

Boiler Room is a newsletter on agentic software development, published on this site under
writings at /writings/boiler-room/ every Monday and Thursday (Monday, Wednesday and Friday until
Nov 27, 2026), with an audio edition and a
podcast feed (/writings/boiler-room/feed.xml). A scheduled task does each edition end to end by
following this file. `scripts/` is excluded from the site build.

## Rules for everything that goes on the site
- Written for a general engineering audience. Never mention the site owner, his employer, his
  product or his team, and nothing personal (routine, location). `publish_edition.py` refuses
  editions that do; rephrase rather than work around it. News about the owner's employer goes in
  the private notes, never on the site.
- No line about how the edition is made (no "compiled with AI", no "synthetic voice").
- Paraphrase everything. At most one quote per source, under 15 words.
- Link the original source (company blog, changelog, release notes, the author's own post)
  wherever one exists. Only use a news article when there is no original. Never invent a URL:
  link only pages you opened or that came back in search results. If a claim can't be traced to
  a source, cut it.
- "Agent app launches" is a plain list of dated launches: who shipped what, with a link. No
  comparisons, no rankings, no commentary.
- Episodes stay under 10 minutes.

## Steps

1. **Date and window.** `today=$(TZ=America/Los_Angeles date +%F)`. If `_boiler_room/$today.md`
   exists, stop: the edition is already out. The window runs from the newest existing edition's
   date to now. Read the two newest editions so you don't repeat their items (a real development in
   a continuing story is fine). Read `scripts/boiler_room/topics.md`.

2. **Research** (at least 30 searches, and as many fetches as the stories need; explore widely, well
   beyond the sites below). Check every one of these for posts in the window:
   - Anthropic and Claude: anthropic.com/news, anthropic.com/engineering, claude.com/blog,
     the Claude Code changelog (code.claude.com/docs/en/changelog), Claude Platform release notes
   - OpenAI: openai.com/news, the OpenAI developer blog (developers.openai.com), the Codex
     changelog (developers.openai.com/codex/changelog)
   - Lenny's Newsletter, The Pragmatic Engineer, Addy Osmani (addyosmani.com/blog), the Warp blog
     (warp.dev/blog)
   - Simon Willison (simonwillison.net), Latent Space, martinfowler.com, Google (Gemini release
     notes and blogs), Cursor, GitHub, Cognition/Devin, the releases.sh coding-agents weekly
     digest, Hacker News front page
   Then search for each "Systems to track" and "Emerging" entry in topics.md, and run at least
   three open searches for things not on the list (new agent apps, new coding agents, new terms
   practitioners are using). The edition should follow where the field is going, not just the
   list.

   **No permission prompts.** The run is unattended, and every page that needs approval sends the
   owner a prompt. Fetch only URLs that came back in a WebSearch result during this run (find each
   source above by searching for it first), or the exact URLs written in the task prompt. When a
   page or a helper's report points to another URL (a post linked from an index page, the original
   behind a digest or a release mirror), first run
   a WebSearch for its title or exact URL and fetch it from that result. Never hand-build, edit or
   guess a URL. When briefing a fetch helper, tell it the same: fetch only the URLs you give it, and
   report other links it finds instead of opening them. If a fetch is refused or asks for approval,
   don't wait or retry it; find the fact through another search result, or cut it.

3. **Write the edition JSON** (`/tmp/br/$today/edition.json`). Use the newest edition's front
   matter as the template; the fields are the same:
   id, number (previous + 1), date, weekday, covers ("Nov 2 – Nov 17, 2026"), title (a short
   thesis, 7 words or fewer), dek (1–2 sentences), key_ideas (3–4 × {title, body ≤ 45 words}),
   sections in this order:
   - `news` "News & launches": 3–6 items
   - `practices` "Practices & playbooks": 3–6 items (playbooks, case studies with numbers,
     techniques a team can adopt)
   - `launches` "Agent app launches": 1–4 dated items, factual only; tag like "Nov 13 · Company"
   - `try` "Try this week": exactly 1 item with tag, headline, body, steps (3–5), measure, links
   Each item: {tag, headline, body ≤ 70 words, links: [{label, url}]}. Optional further_reading
   (0–3 deeper reads). sources: every page relied on, {title, publisher, date, url}.

4. **Write the script** (`/tmp/br/$today/script.txt`): one narrator, 1,150–1,350 words (about 8–9 minutes; the publish script rejects 10 minutes or more). Open with
   "Good morning. This is Boiler Room, a brief on agentic software development.", the weekday,
   date and edition number, and the day's thread in one or two sentences. Then section markers on
   their own lines: `--- News`, `--- Practices`, `--- Launches`, `--- Try this week`, `--- Outro`.
   The outro is two short lines and names the next edition day (Monday → Thursday,
   Thursday → Monday, Friday → Monday). Write for the ear: short sentences; no URLs, markdown,
   bullets, parentheses or symbols; spell out numbers, prices and versions ("GPT six point two",
   "eight dollars per million input tokens"); say acronyms as letters ("M C P", "O-Auth"); say
   "pull request" rather than PR and "agents file" for AGENTS.md. Same facts as the JSON, nothing
   extra.

5. **Record.** `pip install --break-system-packages -q kokoro-onnx soundfile pyyaml`, then
   `python3 scripts/boiler_room/render_audio.py /tmp/br/$today/script.txt /tmp/br/$today/ep.mp3 --voice af_heart --title "Boiler Room No. NNN: <title>" > /tmp/br/$today/render.json`
   It downloads the voice model from GitHub releases on first use and takes about 15 minutes; run
   it in the foreground with a 40-minute timeout. If the episode is 600 seconds or longer, cut
   the script and record again.

6. **Publish.** From the repo root:
   `python3 scripts/boiler_room/publish_edition.py /tmp/br/$today/edition.json /tmp/br/$today/ep.mp3 /tmp/br/$today/render.json --script /tmp/br/$today/script.txt`
   Fix whatever it reports and run it again.

7. **Evolve the watchlist.** Update `scripts/boiler_room/topics.md`: add systems or terms that
   showed up in two or more independent sources this window to "Emerging"; promote an emerging
   entry to core or to "Systems to track" once it has been covered in three or more editions; move
   entries with nothing new for about four weeks to "Retired" with the edition number. Keep the
   whole list under 30 entries and update the "Last updated" line.

8. **Ship.** `git add _boiler_room assets/boiler-room scripts/boiler_room/topics.md`, commit as
   "Boiler Room No. NNN: <title>", and push to main (GitHub Pages deploys it in a minute or two).
   If the push is rejected, fetch, rebase onto origin/main and push again.
   Then check https://arpit-jain.com/writings/boiler-room/ lists the new edition (it can take a
   couple of minutes to appear).
