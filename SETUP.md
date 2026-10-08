# Apply to codingkiddo/codingkiddo

1. Back up your current profile README.
2. Copy README.md, scripts/, assets/, and .github/workflows/profile-impact.yml into the codingkiddo/codingkiddo repository. Preserve unrelated files and workflows.
3. Commit and push to the default branch.
4. In GitHub Actions, select **Update open-source impact graph → Run workflow**. This generates the first graph and commits it. Subsequent refreshes run weekly.

The graph is generated from live GitHub search, not from the old README's PR list. It covers public merged PRs authored by codingkiddo in repositories owned by others, including forks owned by others. It shows the top 15 repositories and groups the remainder. The included SVG was generated from live GitHub search on 2026-10-08: 47 merged PRs across 28 external repositories. The workflow refreshes these counts.

The workflow uses GitHub's built-in token; no personal access token is required. Repository policies or branch protection may prevent its direct push. In that case, generate the SVG locally with `python scripts/update_impact.py` and commit it through your usual process. A token supplied through GITHUB_TOKEN can raise API limits; never commit tokens.

Incomplete results, changing pagination counts, API errors, and more than 1,000 search results fail the update and preserve the previous graph. Counts reflect GitHub's search index and can lag merges.

Suggested profile bio:

Senior Software Engineer @ Airties | Java, Spring & Distributed Systems | Device Intelligence, Cybersecurity & AI Platforms | Open Source Contributor

Suggested pins: taxi-mono-repo, banking-demo, spring-boot-custom-starter; add your telemetry and AI gateway projects when public and documented.
