#!/usr/bin/env python3
"""Turn a Boiler Room edition into site files.

Usage (from the repo root):
  python3 scripts/boiler_room/publish_edition.py EDITION.json EPISODE.mp3 RENDER.json [--script SCRIPT.txt]

- Checks the edition (structure, links, length) and refuses anything personal (see BANNED).
- Copies the MP3 to assets/boiler-room/audio/<id>.mp3 and writes _boiler_room/<id>.md
  (YAML front matter only; _layouts/boiler-edition.html renders it).
- Keeps audio for the newest KEEP_AUDIO editions; older editions stay as text.
Exits non-zero with a reason if anything is wrong; nothing is written in that case.
"""
import argparse, json, re, shutil, sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[2]
COLL = ROOT / "_boiler_room"
AUDIO = ROOT / "assets" / "boiler-room" / "audio"
KEEP_AUDIO = 36          # about 12 weeks at three a week
MAX_SECONDS = 599        # episodes stay under 10 minutes
SECTION_ORDER = ["news", "practices", "launches", "try"]

# Nothing personal and nothing about the owner's employer, product or team on the public site.
BANNED = [
    (r"\bQuick\b", "the word 'Quick' (capitalised)"),
    (r"\bAWS\b", "AWS"), (r"\bAmazon\b", "Amazon"),
    (r"\bArpit\b", "the site owner's name"), (r"\bJain\b", "the site owner's name"),
    (r"\bSeattle\b", "a personal location"),
    (r"(?i)\b(my|our) (team|teams|pods?|org|company|manager|reports)\b", "first-person team references"),
    (r"(?i)\bcommut(e|ing)\b|\bwalk(ing)? (in|to) (the )?(office|work)\b", "personal routine"),
    (r"(?i)compiled with ai|synthetic voice|ai[- ]generated", "a disclosure line the owner asked to leave out"),
]


def fail(msg):
    print(f"publish_edition: {msg}", file=sys.stderr)
    sys.exit(1)


def text_of(obj):
    if isinstance(obj, dict):
        return " ".join(text_of(v) for k, v in obj.items() if k not in ("url", "file"))
    if isinstance(obj, list):
        return " ".join(text_of(v) for v in obj)
    return str(obj) if obj is not None else ""


def check(ed, script_text):
    for k in ("id", "number", "title", "dek", "covers", "key_ideas", "sections", "sources"):
        if not ed.get(k):
            fail(f"missing '{k}'")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ed["id"]):
        fail("id must be YYYY-MM-DD")
    ids = [s.get("id") for s in ed["sections"]]
    if ids != SECTION_ORDER:
        fail(f"sections must be {SECTION_ORDER} in that order, got {ids}")
    if not 3 <= len(ed["key_ideas"]) <= 4:
        fail("key_ideas needs 3 or 4 entries")
    for s in ed["sections"]:
        if not s.get("label") or not s.get("items"):
            fail(f"section '{s.get('id')}' needs a label and items")
        for it in s["items"]:
            if not it.get("headline") or not (it.get("body") or it.get("steps")):
                fail(f"an item in '{s['id']}' needs a headline and a body")
    try_items = ed["sections"][-1]["items"]
    if len(try_items) != 1 or not try_items[0].get("steps") or not try_items[0].get("measure"):
        fail("'try' needs exactly one item with steps and measure")
    urls = []
    def walk(o):
        if isinstance(o, dict):
            if "url" in o:
                urls.append(o["url"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk({k: v for k, v in ed.items() if k != "audio"})
    bad = [u for u in urls if not re.match(r"^https://[^\s\"'<>]+$", str(u))]
    if bad:
        fail(f"links must be https URLs: {bad[:3]}")
    blob = text_of(ed) + " " + (script_text or "")
    for pat, why in BANNED:
        m = re.search(pat, blob)
        if m:
            fail(f"refusing to publish: found {why} ('{m.group(0)}'). Rephrase or move it to the private notes.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edition")
    ap.add_argument("mp3")
    ap.add_argument("render")
    ap.add_argument("--script")
    a = ap.parse_args()

    ed = json.loads(Path(a.edition).read_text(encoding="utf-8"))
    render = json.loads(Path(a.render).read_text(encoding="utf-8"))
    script_text = Path(a.script).read_text(encoding="utf-8") if a.script else ""
    check(ed, script_text)

    dur = float(render["duration_sec"])
    if dur > MAX_SECONDS:
        fail(f"episode is {dur:.0f}s; it must be under 10 minutes. Shorten the script and re-render.")
    mp3 = Path(a.mp3)
    if not mp3.exists() or mp3.stat().st_size < 100_000:
        fail("MP3 missing or too small")

    eid = ed["id"]
    y, m, d = map(int, eid.split("-"))
    # Stamp with the real publish time: Jekyll hides documents dated in the future (future: false),
    # so a stamp ahead of the build time would keep the edition off the site until the next build.
    stamp = (datetime.now(ZoneInfo("America/Los_Angeles")) - timedelta(minutes=2)).replace(second=0, microsecond=0)
    chapters = [c for c in render.get("chapters", []) if c.get("label", "").lower() != "outro"]

    fm = {
        "title": ed["title"],
        "edition_id": eid,
        "number": int(ed["number"]),
        "date": stamp.strftime("%Y-%m-%d %H:%M:%S %z"),
        "weekday": ed.get("weekday") or datetime(y, m, d).strftime("%A"),
        "covers": ed["covers"],
        "dek": ed["dek"],
        "description": ed["dek"],
        "audio": {
            "file": f"/assets/boiler-room/audio/{eid}.mp3",
            "duration_sec": round(dur, 1),
            "bytes": mp3.stat().st_size,
        },
        "chapters": chapters,
        "key_ideas": ed["key_ideas"],
        "sections": ed["sections"],
        "further_reading": ed.get("further_reading", []),
        "sources": ed["sources"],
    }

    COLL.mkdir(exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(mp3, AUDIO / f"{eid}.mp3")
    body = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=10_000)
    (COLL / f"{eid}.md").write_text(f"---\n{body}---\n", encoding="utf-8")

    # Retention: audio for the newest KEEP_AUDIO editions only.
    eds = sorted(COLL.glob("*.md"), reverse=True)
    retired = []
    for p in eds[KEEP_AUDIO:]:
        raw = p.read_text(encoding="utf-8")
        _, front, rest = raw.split("---\n", 2)
        data = yaml.safe_load(front)
        if data.get("audio", {}).get("file"):
            f = ROOT / data["audio"]["file"].lstrip("/")
            if f.exists():
                f.unlink()
            data["audio"]["file"] = None
            p.write_text("---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=10_000) + "---\n" + rest, encoding="utf-8")
            retired.append(p.stem)

    print(json.dumps({"written": f"_boiler_room/{eid}.md", "audio": f"assets/boiler-room/audio/{eid}.mp3",
                      "duration_sec": round(dur, 1), "audio_retired": retired}))


if __name__ == "__main__":
    main()
