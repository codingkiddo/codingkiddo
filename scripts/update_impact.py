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
    return list(items.values())


def render(items, date):
    today = datetime.date.fromisoformat(date)
    start = today - datetime.timedelta(days=364)
    origin = start - datetime.timedelta(days=(start.weekday() + 1) % 7)
    counts = collections.Counter(item["repository_url"].split("/repos/", 1)[1] for item in items)
    daily = collections.Counter()
    for item in items:
        merged = item["pull_request"].get("merged_at")
        if not merged:
            raise RuntimeError("Missing merge date; keeping previous graph.")
        daily[datetime.date.fromisoformat(merged[:10])] += 1
    recent = sum(n for day, n in daily.items() if start <= day <= today)
    active = sum(1 for day in daily if start <= day <= today)
    colors = ["#172a3a", "#176b62", "#209b78", "#48d6a0", "#a0ffce"]
    def level(n):
        return 0 if n == 0 else 1 if n == 1 else 2 if n <= 3 else 3 if n <= 5 else 4
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="490" viewBox="0 0 1100 490" role="img" aria-labelledby="title desc">',
        '<title id="title">Open-source contribution calendar</title>',
        f'<desc id="desc">{len(items)} public merged pull requests across {len(counts)} external repositories. Calendar shows {recent} merges on {active} days in the last 365 days, by UTC merge date.</desc>',
        '<rect width="1100" height="490" rx="20" fill="#0d1520"/>',
        '<g font-family="Arial, sans-serif" fill="#e6edf3">',
        '<text x="36" y="42" font-size="12" letter-spacing="3" fill="#48d6a0">CODINGKIDDO / OPEN SOURCE</text>',
        '<text x="36" y="78" font-size="27" font-weight="bold">Small fixes. Lasting impact.</text>']
    for i, (value, label) in enumerate([(len(items), "MERGED PRs · ALL TIME"), (len(counts), "EXTERNAL REPOSITORIES"), (recent, "MERGES · LAST 365 DAYS")]):
        x = 36 + 345 * i
        parts.extend([f'<rect x="{x}" y="104" width="326" height="86" rx="12" fill="#132232" stroke="#243749"/>',
            f'<text x="{x+18}" y="143" font-size="30" font-weight="bold">{value}</text>',
            f'<text x="{x+18}" y="170" font-size="11" letter-spacing="1" fill="#9fb3c8">{label}</text>'])
    parts.append('<text x="36" y="226" font-size="14" fill="#9fb3c8">Merge activity / rolling year</text>')
    for offset in range((today-origin).days+1):
        day = origin + datetime.timedelta(days=offset)
        if day < start:
            continue
        week, weekday = divmod(offset, 7)
        n = daily[day]
        # A shallow isometric projection; raised cells encode daily merges.
        x, y = 120 + week * 16 + weekday * 11, 260 + weekday * 8 - week * 0.28
        lift = min(n, 8) * 2
        points = f"{x},{y-lift} {x+14},{y-4-lift} {x+24},{y+3-lift} {x+10},{y+7-lift}"
        parts.append(f'<g><title>{day}: {n} merged PRs</title>')
        if lift:
            parts.append(f'<polygon points="{x+10},{y+7-lift} {x+24},{y+3-lift} {x+24},{y+3} {x+10},{y+7}" fill="#176b62"/>')
            parts.append(f'<polygon points="{x},{y-lift} {x+10},{y+7-lift} {x+10},{y+7} {x},{y}" fill="#10463f"/>')
        parts.append(f'<polygon points="{points}" fill="{colors[level(n)]}" stroke="#0d1520" stroke-width="1"/></g>')
        if weekday == 0 and day.day <= 7:
            parts.append(f'<text x="{x}" y="{y+99}" font-size="11" fill="#9fb3c8">{day.strftime("%b")}</text>')
    parts.append('<text x="36" y="396" font-size="12" fill="#9fb3c8">Each tile is one day · height and color show merged contributions</text>')
    for i, color in enumerate(colors):
        parts.append(f'<rect x="{837+i*25}" y="384" width="18" height="14" rx="3" fill="{color}"/>')
    parts.extend(['<text x="798" y="396" font-size="11" fill="#9fb3c8">Less</text>',
        '<text x="970" y="396" font-size="11" fill="#9fb3c8">More</text>',
        '<path d="M36 421 H1064" stroke="#243749"/>',
        f'<text x="36" y="454" font-size="12" fill="#9fb3c8">Public repositories owned by others · actual UTC merge dates · updated {date}</text>',
        '</g></svg>'])
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    items = fetch()
    svg = render(items, datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Generated calendar: {len(items)} merged PRs")
