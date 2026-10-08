"""Generate a self-contained SVG from public merged PRs; no dependencies."""
import collections
import datetime
import html
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

USER = "codingkiddo"
OUTPUT = Path(__file__).resolve().parents[1] / "assets/open-source-impact.svg"


def fetch():
    items = {}
    expected = None
    for page in range(1, 11):
        query = urllib.parse.urlencode({
            "q": f"is:pr is:merged is:public author:{USER} -user:{USER}",
            "per_page": 100, "page": page, "sort": "created", "order": "asc",
        })
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "codingkiddo-profile"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request("https://api.github.com/search/issues?" + query, headers=headers)
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.load(response)
        if data.get("incomplete_results") or data["total_count"] > 1000:
            raise RuntimeError("Incomplete GitHub search; keeping the previous graph. Narrow the date range before retrying.")
        if expected is None:
            expected = data["total_count"]
        if data["total_count"] != expected:
            raise RuntimeError("Search changed while paging; rerun to obtain consistent counts.")
        for item in data["items"]:
            items[item["id"]] = item
        if len(items) >= expected:
            break
        if not data["items"]:
            raise RuntimeError("Missing search results; keeping previous graph.")
    if len(items) != expected:
        raise RuntimeError("Search count mismatch; keeping previous graph.")
    return collections.Counter(item["repository_url"].split("/repos/", 1)[1] for item in items.values())


def render(counts, date):
    rows = sorted(counts.items(), key=lambda row: (-row[1], row[0]))[:15]
    remaining = sum(counts.values()) - sum(n for _, n in rows)
    if remaining:
        rows.append(("Other repositories", remaining))
    height = 180 + 35 * len(rows)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Merged open-source contributions by repository</title>',
        f'<desc id="desc">{sum(counts.values())} public merged pull requests across {len(counts)} external repositories. Updated {date}.</desc>',
        f'<rect width="1000" height="{height}" rx="16" fill="#0d1117"/>',
        '<g font-family="Arial, sans-serif" fill="#e6edf3">',
        '<text x="30" y="42" font-size="23" font-weight="bold">Open-source impact</text>',
        f'<text x="30" y="73" font-size="16">{sum(counts.values())} merged PRs · {len(counts)} repositories</text>']
    maximum = max((n for _, n in rows), default=1)
    for index, (repo, count) in enumerate(rows):
        y = 112 + index * 35
        parts.extend([f'<text x="30" y="{y + 17}" font-size="13">{html.escape(repo)}</text>',
            f'<rect x="440" y="{y}" width="{460 * count / maximum:.1f}" height="23" rx="4" fill="#58a6ff"/>',
            f'<text x="920" y="{y + 17}" font-size="14">{count}</text>'])
    if not rows:
        parts.append('<text x="30" y="120" font-size="15">No matching public merged contributions found.</text>')
    parts.extend([f'<text x="30" y="{height - 23}" font-size="12" fill="#8b949e">Public external repositories · top 15 + others · updated {date} UTC</text>', '</g></svg>'])
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    counts = fetch()
    svg = render(counts, datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Generated graph: {sum(counts.values())} merged PRs across {len(counts)} repositories")
